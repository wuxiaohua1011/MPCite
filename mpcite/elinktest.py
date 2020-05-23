import requests
import json
from xmltodict import parse
from xml.dom.minidom import parseString
import logging

elink_endpoint = "https://www.osti.gov/elinktest/2416api"
username = "materials2416websvs"
password = "Sti!2416sub"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


data = b'<?xml version="1.0" ?><records><record><dataset_type>SM</dataset_type><title>Materials Data on Mg(SbO2)2 by Materials Project</title><creators>Kristin Persson</creators><product_nos>mp-1388665</product_nos><accession_num>mp-1388665</accession_num><contract_nos>AC02-05CH11231; EDCBEE</contract_nos><originating_research_org>Lawrence Berkeley National Laboratory (LBNL), Berkeley, CA (United States)</originating_research_org><publication_date>05/02/2020</publication_date><language>English</language><country>US</country><sponsor_org>USDOE Office of Science (SC), Basic Energy Sciences (BES) (SC-22)</sponsor_org><site_url>https://materialsproject.org/materials/mp-1388665</site_url><contact_name>Kristin Persson</contact_name><contact_org>LBNL</contact_org><contact_email>kapersson@lbl.gov</contact_email><contact_phone>+1(510)486-7218</contact_phone><related_resource>https://materialsproject.org/citing</related_resource><contributor_organizations>MIT; UC Berkeley; Duke; U Louvain</contributor_organizations><subject_categories_code>36 MATERIALS SCIENCE</subject_categories_code><keywords>crystal structure; Mg(SbO2)2; Mg-O-Sb; electronic bandstructure</keywords><description>Computed materials data using density functional theory calculations. These calculations determine the electronic structure of bulk materials by solving approximations to the Schrodinger equation. For more information, see https://materialsproject.org/docs/calculations</description></record></records>'


def post():
    logging.debug("POSTING")
    r = requests.post(elink_endpoint, auth=(username, password), data=data)
    return r


if __name__ == "__main__":
    dom = parseString(data)

    # print("*************")
    # print("I'm posting the data below")
    # print(dom.toprettyxml())
    # print("*************")

    r = post()

    print("**********************")
    print("Results from posting: ")
    print("status_code = ", r.status_code)
    import json

    print(f"content = {json.dumps(parse(r.content), indent=2)}")
    print("**********************")