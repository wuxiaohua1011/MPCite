from maggma.stores.advanced_stores import MongograntStore

dois_store = MongograntStore(
    mongogrant_spec="readWrite:knowhere.lbl.gov/mp_core_mwu", collection_name="dois"
)
materials_store = MongograntStore(
    mongogrant_spec="read:knowhere.lbl.gov/mp_core",
    collection_name="materials_2020_09_04",
)
dois_store.connect()
materials_store.connect()
pending_dois = dois_store.query(criteria={"status": "PENDING"})

materials = []
for pending_doi in pending_dois:
    material = materials_store.query_one(
        criteria={
            "$and": [
                {"task_id": pending_doi["material_id"]},
                {"sbxd.id": "core"},
                {"sbxn": "core"},
            ]
        },
        properties={"task_id": 1},
    )
    if material is None:
        print(pending_doi)
    else:
        print("this material is okay -> ", material["task_id"])
    materials.append(material)
