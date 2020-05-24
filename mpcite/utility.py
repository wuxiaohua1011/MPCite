from models import *
from abc import abstractmethod, ABCMeta
from typing import Union, List
import logging
import requests
from urllib3.exceptions import HTTPError
from xmltodict import parse
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString


class Adapter(metaclass=ABCMeta):
    def __init__(self, config: ConnectionModel):
        self.config = config
        logging.getLogger("urllib3").setLevel(logging.ERROR)  # forcefully disable logging from urllib3
        logging.getLogger("dicttoxml").setLevel(logging.ERROR)  # forcefully disable logging from dicttoxml
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def post(self, data):
        pass

    @abstractmethod
    def get(self, params):
        pass


class ELinkAdapter(Adapter):
    INVALID_URL_STATUS_MESSAGE = "URL entered is invalid or unreachable."

    def post(self, data: bytes) -> List[ELinkPostResponseModel]:
        r = requests.post(self.config.endpoint, auth=(self.config.username, self.config.password), data=data)
        if r.status_code != 200:
            self.logger.error(f"POST for {data} failed")
            raise HTTPError(f"POST for {data} failed")
        else:
            content: Dict[str, Dict[str, ELinkPostResponseModel]] = parse(r.content)
            if content["records"] is None:
                raise HTTPError(f"POST for {data} failed due to content['records'] is None")
            to_return = []
            for _, elink_responses in content["records"].items():
                if type(elink_responses) == list:
                    for elink_response in elink_responses:
                        e = self.parse_obj_to_elink_post_response_model(elink_response)
                        if e is not None:
                            to_return.append(e)
                else:
                    e = self.parse_obj_to_elink_post_response_model(elink_responses)
                    if e is not None:
                        to_return.append(e)
            return to_return

    def parse_obj_to_elink_post_response_model(self, obj) -> Union[None, ELinkPostResponseModel]:
        try:
            elink_response_record = ELinkPostResponseModel.parse_obj(obj)
            return elink_response_record
        except Exception as e:
            self.logger.error(f"Skipping. Error:{e}.\n Cannot Parse the received Elink Response: \n{elink_response} ")
            return None

    @classmethod
    def prep_posting_data(cls, items: List[dict]) -> bytes:
        """
        using dicttoxml and customized xml configuration to generate posting data according to Elink Specification
        :param items: list of dictionary of data
        :return:
            xml data in bytes, ready to be sent via request module
        """

        xml = dicttoxml(items, custom_root='records', attr_type=False)
        records_xml = parseString(xml)
        items = records_xml.getElementsByTagName('item')
        for item in items:
            records_xml.renameNode(item, '', item.parentNode.nodeName[:-1])
        return records_xml.toxml().encode('utf-8')

    def get(self, mpid_or_ostiid: str) -> Union[None, ELinkGetResponseModel]:
        key = 'site_unique_id' if 'mp-' in mpid_or_ostiid or 'mvc-' in mpid_or_ostiid else 'osti_id'
        payload = {key: mpid_or_ostiid}
        self.logger.debug('GET from {} w/i payload = {} ...'.format(self.config.endpoint, payload))
        r = requests.get(self.config.endpoint, auth=(self.config.username, self.config.password), params=payload)
        if r.status_code == 200:
            elink_response_xml = r.content
            return ELinkGetResponseModel.parse_obj(parse(elink_response_xml)["records"]["record"])
        else:
            msg = f"Error code from GET is {r.status_code}"
            self.logger.error(msg)
            raise HTTPError(msg)

    def get_multiple(self, mpid_or_ostiids: List[str]) -> List[ELinkGetResponseModel]:
        result: List[ELinkGetResponseModel] = []
        for mpid_or_ostiid in mpid_or_ostiids:
            try:
                r = self.get(mpid_or_ostiid=mpid_or_ostiid)
                result.append(r)
            except HTTPError as e:
                self.logger.error(f"Skipping [{mpid_or_ostiid}]. Error: {e}")
        return result

    def get_multiple_in_dict(self, mpid_or_ostiids: List[str]) -> Dict[str, ELinkGetResponseModel]:
        return {r.accession_num: r for r in self.get_multiple(mpid_or_ostiids=mpid_or_ostiids)}


class ExplorerAdapter(Adapter):

    def post(self, data):
        pass

    def get(self, params):
        pass


class ElviserAdapter:
    pass
