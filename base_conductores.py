import json
import os
from base_de_datos import BaseDeDatos

#JSON_FILES_PATH = os.path.join(os.path.dirname(__file__), "../../../../JsonFiles/")
#from uc3m_logistics.exception.order_management_exception import OrderManagementException


class BaseDeConductores(BaseDeDatos):
    """
    Json store master
    """
    
    _data_list = []
    __ERROR_MESSAGE_PATH = "Wrong file or file path"
    __ERROR_JSON_DECODE = "JSON Decode Error - Wrong JSON Format"
    FILE_PATH = os.path.dirname(__file__) + "\\Bases\\conductores.json"
    ID_FIELD = "id"

    def __init__(self):
        super(BaseDeDatos, self).__init__()

    def find_data_ruta(self, origen, destino: any) :
        """
        find data
        """
        self.load_store()
        item_found = []
        for item in self._data_list:
            if item["ruta_origen"] == origen and item["ruta_destino"] == destino and item["contador"] > 0:
                item_found.append(item)
        return item_found
    
    def find_data_id(self, id: any):
        """
        find data
        """
        self.load_store()
        for item in self._data_list:
            if item["id"] == id:   
                return item
        return None
