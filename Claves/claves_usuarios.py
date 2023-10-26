import json
import os
from Datos.base_de_datos import BaseDeDatos

class ClavesUsuarios(BaseDeDatos):
    """
    Json store master
    """
    
    _data_list = []
    __ERROR_MESSAGE_PATH = "Wrong file or file path"
    __ERROR_JSON_DECODE = "JSON Decode Error - Wrong JSON Format"
    FILE_PATH = os.path.dirname(__file__) + "/Bases/claves_usuarios.json"
    ID_FIELD = "Correo"

    def __innit__(self):
        super(BaseDeDatos, self).__innit__()