import json
import os
from base_de_datos import BaseDeDatos

#JSON_FILES_PATH = os.path.join(os.path.dirname(__file__), "../../../../JsonFiles/")
#from uc3m_logistics.exception.order_management_exception import OrderManagementException


class BaseDeUsuarios(BaseDeDatos):
    """
    Json store master
    """
    
    _data_list = []
    __ERROR_MESSAGE_PATH = "Wrong file or file path"
    __ERROR_JSON_DECODE = "JSON Decode Error - Wrong JSON Format"
    FILE_PATH = "/DATOS/BELÉN/3º UNI/Criptografía/Practica_1/Criptografia/registro_usuarios.json"
    ID_FIELD = "Correo"

    def __innit__(self):
        super(BaseDeDatos, self).__innit__()