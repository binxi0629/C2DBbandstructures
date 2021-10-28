import ase.db
from c2dbjson import C2DBjson

def main():

    db = ase.db.connect('c2db-2021-06-24.db')
    # db = ase.db.connect('c2db.db')
    type_list = ["results-asr.database.material_fingerprint.json", "results-asr.structureinfo.json", "results-asr.bandstructure.json"]
    json_keys = {"uid": "results-asr.database.material_fingerprint.json", "structure": "results-asr.structureinfo.json", "bands": "results-asr.bandstructure.json"}

    rows = db.select("")
    count = 0
    invalid = 0
    invalid_list = []

    print("Loading...")
    for row in rows:
        # print(row)
        c2db_datajson = {}
        # create c2db class
        c2db_data = C2DBjson(uid=row.uid, save_path='c2db_database/')
        c2db_data.getInfoType(type_list=type_list)

        # exrtact necessary info
        try:
            c2db_dict = c2db_data.getJsonbyTypeList()
        except AssertionError:
            # print(f"Band Structure Not Found for uid{c2db_data.item}")
            invalid += 1
            invalid_list.append(c2db_data.item)
            continue
        # save
        for each_k in json_keys.keys():
            c2db_datajson[each_k] = c2db_dict[json_keys[each_k]]

        c2db_data.writeJsonFile(c2db_datajson)
        count += 1
        print(f"\r\t Finished:  {count} |    Invalid:   {invalid} |   Total:  4056", end='')
        # print(row.uid)

    print("Invalid uid list: ", invalid_list)


if __name__ == '__main__':
    main()
