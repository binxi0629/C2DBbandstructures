from urllib import request
import requests
import urllib.error
import http.client

import numpy as np
import json, re, os


class C2DBjson:

    _base_url = 'https://cmrdb.fysik.dtu.dk/c2db/row/'

    def __init__(self, uid:str, save_path='./'):

        self.item = uid
        self.url=f"{C2DBjson._base_url}{self.item}/data"
        self.type_list:list

        self._c2db_type__ = {"info.json":C2DBjson.getInfoJson,
                             "results-asr.bader.json": C2DBjson.getBaderJson,
                             "results-asr.bandstructure.json": C2DBjson.getBandStructureJson,
                             "results-asr.bandstructure@calculate.json":C2DBjson.getBandStructureCalJson,
                             "results-asr.convex_hull.json": C2DBjson.getConvex_hullJson,
                             "results-asr.database.material_fingerprint.json": self.getDatabaseMaterial_fringerprintJson,
                             "results-asr.exchange.json":C2DBjson.getExchangeJson,
                             "results-asr.exchange@calculate.json": C2DBjson.getExchangeCalJson,
                             "results-asr.gs.json":C2DBjson.getGsJson,
                             "results-asr.gs@calculate.json": C2DBjson.getGsCalJson,
                             "results-asr.magnetic_anisotropy.json": C2DBjson.getMagnetic_anisotropyJson,
                             "results-asr.magstate.json": C2DBjson.getMagstateJson,
                             "results-asr.pdos.json": C2DBjson.getPdosJson,
                             "results-asr.pdos@calculate.json":C2DBjson.getPdosCalJson,
                             "results-asr.phonons.json": C2DBjson.getPhononsJson,
                             "results-asr.phonons@calculate.json": C2DBjson.getPhononsCalJson,
                             "results-asr.plasmafrequency.json": C2DBjson.getPlasmafrequencyJson,
                             "results-asr.plasmafrequency@calculate.json": C2DBjson.getPlasmafrequencyCalJson,
                             "results-asr.polarizability.json":C2DBjson.getPlorizabilityJson,
                             "results-asr.projected_bandstructure.json": C2DBjson.getProjected_bandstructureJson,
                             "results-asr.relax.json": C2DBjson.getRelaxJson,
                             "results-asr.setinfo.json": C2DBjson.getSetinfoJson,
                             "results-asr.setup.reduce.json": C2DBjson.getSetupReduceJson,
                             "results-asr.setup.strains.json": C2DBjson.getSetupStrainsJson,
                             "results-asr.stiffness.json": C2DBjson.getStiffnessJson,
                             "results-asr.structureinfo.json":C2DBjson.getStructureinfoJson,
                             "structure.json": C2DBjson.getStructureJson}
        self.save_path = save_path
        self.jsonfile_name = f"c2db_{uid}.json"

    def writeJsonFile(self, jsonfile:dict):
        with open(os.path.join(self.save_path,self.jsonfile_name),'w') as jf:
            json.dump(jsonfile, jf, cls=NumpyEncoder, indent=2)


    def getInfoType(self, type_list):
        if 0==len(type_list):
            raise ("JSON FILE NOT DEFINED, please define a json file type and refere: https://cmrdb.fysik.dtu.dk/c2db/row/Ag2F4-8e332582f342/data")

        self.type_list = type_list
        for eachType in self.type_list:
            if eachType not in self._c2db_type__ or '' == eachType:
                raise ("JSON FILE NOT FOUND, check the corresponding json type here: https://cmrdb.fysik.dtu.dk/c2db/row/Ag2F4-8e332582f342/data")

    def getJsonbyTypeList(self):
        """

        :return: tmp_dict: dict that stores all requried inforamtion
        """
        tmp_dict = {}
        for eachType in self.type_list:
            url = f"{self.url}/{eachType}/json"
            #TODO >>
            tmp_dict[eachType] = self._c2db_type__[eachType](url)
        return tmp_dict

    @staticmethod
    def getJsonByURL(url) -> http.client.HTTPResponse:
        """
        :param url: url links to C2DB(https://cmrdb.fysik.dtu.dk/c2db)
        :return: response: http.client.HTTPResponse Object
        """
        try:
            response = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            if hasattr(e, 'code'):
                print("ERROR CODE", e.code)
            if hasattr(e, "reason"):
                print("ERROR MESSAGE: ", e.reason)
        else:
            return response


    @staticmethod
    def getInfoJson(url):
        """
        :param url: url links to specific C2DB info.json (https://cmrdb.fysik.dtu.dk/c2db/row/<item_uid>/info.json/json)
        :return:
        """
        response = C2DBjson.getJsonByURL(url)
        info = json.loads(response.read())
        checkTypeDict(info)

    @staticmethod
    def getBandStructureJson(url)-> dict:
        """

        :param url:  url links to specific C2DB results-asr.bandstructure.json (https://cmrdb.fysik.dtu.dk/c2db/row/<item_uid>/results-asr.bandstructure.json/json)
        :return: bands: type dict
        """
        bands = {}
        bands["nonsoc_energies"] = {}

        bands["soc_energies"] ={}

        is_spinporlarized = -1 #

        #request data
        response = C2DBjson.getJsonByURL(url)
        bandstructure =json.loads(response.read())

        # check data type matching dict
        # try:
        #     checkTypeDict(bandstructure)
        # except AssertionError:
        #     print("band structure not found")
        #     return None
        # extract band structure
        checkTypeDict(bandstructure)

        try:
            nosoc_target = bandstructure["kwargs"]['data']['bs_nosoc']['energies']["__ndarray__"]
        except KeyError as e:
            nosoc_energies = None
        else:
            nosoc_shape, _, nosoc_energies = nosoc_target[0], nosoc_target[1], np.array(nosoc_target[2])
            if 1==nosoc_shape[0]:
                is_spinporlarized = 0
            elif 2==nosoc_shape[0]:
                is_spinporlarized=1
            else:
                raise ("Spin polarized calculation not known")

            bands["nonsoc_energies"]["kpath"] = {}
            bands["nonsoc_energies"]["is_spinpolarized"] = is_spinporlarized

            nosoc_energies = nosoc_energies.reshape(tuple(nosoc_shape))
            bands["nonsoc_energies"]["bands"] = nosoc_energies

            kpath = bandstructure["kwargs"]['data']['bs_nosoc']["path"]
            kps = kpath["kpts"]["__ndarray__"]
            kps_shape, _, kps_arrays = kps[0], kps[1], np.array(kps[2])
            kps_arrays = kps_arrays.reshape(tuple(kps_shape))
            # print(kps_arrays.shape)

            bands["nonsoc_energies"]["kpath"]["kpoints"] =kps_arrays
            kps_labels = kpath["labelseq"]
            bands["nonsoc_energies"]["koints_labels"]=kps_labels
            bands["nonsoc_energies"]["special_points"] = kpath["special_points"]

        try:
            soc_target = bandstructure["kwargs"]['data']['bs_soc']['energies']["__ndarray__"]
        except KeyError as e:
            soc_energies = None
        else:
            bands["soc_energies"]["kpath"] = {}
            soc_shape, _, soc_energies = soc_target[0], soc_target[1], np.array(soc_target[2])
            soc_energies = soc_energies.reshape(tuple(soc_shape))
            bands["soc_energies"]["bands"] = soc_energies

            #kpath
            kpath2 = bandstructure["kwargs"]['data']['bs_soc']["path"]
            kps2=kpath2["kpts"]["__ndarray__"]

            kps2_shape, _, kps2_arrays = kps2[0], kps2[1], np.array(kps2[2])
            kps_arrays2 = kps2_arrays.reshape(tuple(kps2_shape))
            # print(kps_arrays.shape)
            bands["soc_energies"]["kpath"]["kpoints"] = kps_arrays2
            kps_labels2 = kpath2["labelseq"]
            bands["soc_energies"]["koints_labels"] = kps_labels2
            bands["soc_energies"]["special_points"] = kpath2["special_points"]

        return bands

    @staticmethod
    def getRelaxJson(url):
        relaxedCell = {}

        # request data
        response = C2DBjson.getJsonByURL(url)
        cell_info = json.loads(response.read())

        # print(type(cell_info))
        # print(cell_info)
        # check data type matching dict
        try:
            checkTypeDict(cell_info)
        except AssertionError:
            if cell_info is None:
                print("\r\tNo relaxation information for the current layer strutcure", end='')
                return None
        #extract cell info
        cell = cell_info["kwargs"]["data"]

        #atom positions
        spos_shape, _, supercell_pos = tuple(cell["spos"]["__ndarray__"][0]),cell["spos"]["__ndarray__"][1],np.array(cell["spos"]["__ndarray__"][2])
        supercell_pos = supercell_pos.reshape(spos_shape)

        #atom symbols
        symbols = cell_info["kwargs"]["data"]

        #latiice constant
        a = cell_info["kwargs"]["data"]["a"]
        b = cell_info["kwargs"]["data"]["b"]
        c = cell_info["kwargs"]["data"]["c"]
        alpha = cell_info["kwargs"]["data"]["alpha"]
        beta = cell_info["kwargs"]["data"]["beta"]
        gamma = cell_info["kwargs"]["data"]["gamma"]

        #energy from DFT
        energy_dft = cell_info["kwargs"]["data"]["edft"]

        relaxedCell["symbols"] = symbols
        relaxedCell["lattice_info"] = {}
        relaxedCell["lattice_info"]["a"] = a
        relaxedCell["lattice_info"]["b"] = b
        relaxedCell["lattice_info"]["c"] = c
        relaxedCell["lattice_info"]["alpha"] = alpha
        relaxedCell["lattice_info"]["beta"] = beta
        relaxedCell["lattice_info"]["gamma"] = gamma
        relaxedCell["energy_dft"] = energy_dft
        relaxedCell["supercell_positions"] =supercell_pos

        return relaxedCell



    def getDatabaseMaterial_fringerprintJson(self,url):
        #request
        response = C2DBjson.getJsonByURL(url)
        m_fringerprint = json.loads(response.read())

        # check data type matching dict
        checkTypeDict(m_fringerprint)

        #get uid which should be the same as self.item
        uid_ = str(m_fringerprint["kwargs"]["data"]["uid"])

        if uid_ != self.item:
            print(f"ID not match: get: {uid_}| reqired: {self.item}")

        return uid_

    @staticmethod
    def getStructureinfoJson(url)->dict:
        # request
        response = C2DBjson.getJsonByURL(url)
        structure_info = json.loads(response.read())

        # check data type matching dict
        checkTypeDict(structure_info)

        structure = {}
        formula =  structure_info["kwargs"]["data"]["formula"]
        point_group = structure_info["kwargs"]["data"]["pointgroup"]

        spacegroup = structure_info["kwargs"]["data"]["spacegroup"]

        tmp = structure_info["kwargs"]["data"]["spglib_dataset"]
        spacegroup_num = tmp["number"]
        std_lattice_array = tmp["std_lattice"]["__ndarray__"]
        lattice_shape, _, std_lattice = tuple(std_lattice_array[0]), std_lattice_array[1], np.array(std_lattice_array[2])
        std_lattice = std_lattice.reshape(lattice_shape)

        std_position_array = tmp["std_positions"]["__ndarray__"]
        position_shape, _ , std_position = tuple(std_position_array[0]), std_position_array[1], np.array(std_position_array[2])
        std_position = std_position.reshape(position_shape)

        atom_type_array = tmp["std_types"]["__ndarray__"]
        atom_type = np.array(atom_type_array[2])
        structure["formula"] = formula
        structure["point_group"] = point_group
        structure["spacegroup"] = spacegroup
        structure["spacegroup_number"] =spacegroup_num
        structure["lattice"] = std_lattice
        structure["position"] = std_position
        structure["atom_types"] = atom_type

        return structure


    #TODO: >>>the following methods are not developed, add the costume functionalities for your own use
    @staticmethod
    def getBaderJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getBandStructureCalJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getConvex_hullJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getExchangeJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getExchangeCalJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getGsJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getGsCalJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getMagnetic_anisotropyJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getMagstateJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getPdosJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getPdosCalJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getPhononsJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getPhononsCalJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getPlasmafrequencyJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getPlasmafrequencyCalJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getPlorizabilityJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getProjected_bandstructureJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass


    @staticmethod
    def getSetinfoJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getSetupReduceJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getSetupStrainsJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass

    @staticmethod
    def getStiffnessJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass


    @staticmethod
    def getStructureJson(url):
        print("No effect, to be developed, feel free to add functionalities by yourself")
        pass


def checkTypeDict(data):
    assert (type(data) == dict), f"TYPE NOT dict, get({type(data)}), required dict"


class NumpyEncoder(json.JSONEncoder):
    """
        to solve Error: NumPy array is not JSON serializable
        see: https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable
    """
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


# def test():
#     item_list = ["SeTeTi-03e8a2c97f5b","Br2Cu2Te4-af27d0354197","I2Mo2N2-86ca1139b89c","Cl2Se2Ta2-e57e23a4a52d"]
#
#     type_list = ["results-asr.database.material_fingerprint.json","results-asr.structureinfo.json", "results-asr.bandstructure.json"]
#     json_keys = {  "uid":"results-asr.database.material_fingerprint.json" ,
#                     "structure":"results-asr.structureinfo.json",
#                     "bands":"results-asr.bandstructure.json",
#                     }
#     count = 0
#     total = len(item_list)
#     print("Loading...")
#     for i in item_list:
#         c2db_datajson = {}
#         # create c2db class
#         c2db_data = C2DBjson(uid=i, save_path='c2db_database_test/')
#         c2db_data.getInfoType(type_list=type_list)
#
#         #exrtact necessary info
#         c2db_dict=c2db_data.getJsonbyTypeList()
#
#         #save
#         for each_k in json_keys.keys():
#
#             c2db_datajson[each_k]=c2db_dict[json_keys[each_k]]
#
#         c2db_data.writeJsonFile(c2db_datajson)
#         count +=1
#         print(f"\r\t Finished: {count}|{total}", end='')


def main():
    #test()
    pass

if __name__ == '__main__':
    main()