from base_de_datos import BaseDeDatos
import os

#JSON_FILES_PATH = os.path.join(os.path.dirname(__file__), "../../../../JsonFiles/")
#from uc3m_logistics.exception.order_management_exception import OrderManagementException


class BaseDeUsuarios(BaseDeDatos):
    """
    Json store master
    """
    
    _data_list = []
    __ERROR_MESSAGE_PATH = "Wrong file or file path"
    __ERROR_JSON_DECODE = "JSON Decode Error - Wrong JSON Format"
    FILE_PATH =  os.path.dirname(__file__) + "\\Bases\\registro_usuarios.json"
    ID_FIELD = "Correo"

    def __init__(self):
        super(BaseDeDatos, self).__init__()