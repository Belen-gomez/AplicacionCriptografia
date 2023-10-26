import json
import os
from base_de_datos import BaseDeDatos

#JSON_FILES_PATH = os.path.join(os.path.dirname(__file__), "../../../../JsonFiles/")
#from uc3m_logistics.exception.order_management_exception import OrderManagementException


class BaseDeViajes(BaseDeDatos):
    """
    Json store master
    """
    
    _data_list = []
    __ERROR_MESSAGE_PATH = "Wrong file or file path"
    __ERROR_JSON_DECODE = "JSON Decode Error - Wrong JSON Format"
    ID_FIELD = "Correo"

    def __init__(self):
        super(BaseDeDatos, self).__init__()
        self.FILE_PATH = None
