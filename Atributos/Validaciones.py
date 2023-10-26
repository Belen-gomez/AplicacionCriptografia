import re
import getpass

class ValidarCampos:
    def __init__(self):
        pass
    
    def ComprobarCorreo(self, dato):
        regex = r"^[a-z0-9]+(\.[a-z0-9]+)*[@](\w+[.])+\w{2,3}$"
        myregex = re.compile(regex)
        res = myregex.fullmatch(dato)
        return res
 
    def ComprobarTelefono(self, telefono):
        regex = r"^[67]{1}[0-9]{8}$"
        myregex = re.compile(regex)
        res = myregex.fullmatch(telefono)
        return res
    
    def ComprobarConstrasenia(self, contrasenia):
        regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d\W]{8,}$"
        myregex = re.compile(regex)
        res = myregex.fullmatch(contrasenia)
        return res
    
    def ValidarContrasenia(self, res_contrasenia):
        while not res_contrasenia:
            print("La contraseña no es valida. Debe tener al menos 8 caracteres, una mayuscula, una minuscula y un numero.")
            contrasenia = getpass.getpass("Introduce una nueva contraseña: ")
            res_contrasenia = self.ComprobarConstrasenia(contrasenia)
        return