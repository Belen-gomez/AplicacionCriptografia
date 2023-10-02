"""
1. iniciar sesion
    a. Si no tienes cuenta, registrarse. Guardar la contraseña en una base de datos con el correo y el salt

"""

import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base_de_datos import BaseDeDatos
from excepciones import Excepcion
import getpass
import re

def ComprobarCorreo(correo):
    regex = r"^[a-z0-9]+(\.[a-z0-9]+)*[@](\w+[.])+\w{2,3}$"
    myregex = re.compile(regex)
    res = myregex.fullmatch(correo)
    return res

def Registro():
    print("Registro de usuarios")
    nombre = input("Introducir nombre completo: ")
    correo = input("Introducir correo: ")
    res = ComprobarCorreo(correo)

    while not res:
        print("El correo no es valido")
        correo = input("Vuelve a introducir correo: ")
        res = ComprobarCorreo(correo)
    
    telefono = input("Introducir telefono: ")
    contraseña = getpass.getpass("Introducir contraseña: ")
    contraseña_2 = getpass.getpass("Repite la contraseña: ")
    while contraseña != contraseña_2:
        print("Las contraseñas no coinciden")
        contraseña = input("Vuelve a introducir contraseña: ")
        contraseña_2 = input("Repite la contraseña: ")

    # Guardar la contraseña en una base de datos con el correo y el salt
    salt = os.urandom(16)
    # derive
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = kdf.derive(contraseña.encode())
    # verify
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
   
    if (kdf.verify(contraseña.encode(), key)) is not None:
        raise Excepcion("Fallo en el registro")
    
    nuevo_usuario={"Correo": correo, "Contraseña_derivada": str(key), "Salt": str(salt)}
    bd = BaseDeDatos()
   
    if bd.find_data(correo) is not None:
        print("El usuario ya existe. Inicia sesion con tu cuenta")
        InicioSesion()

    bd.add_item(nuevo_usuario)

def InicioSesion():
    print("Inicio de sesion")
    correo = input("Introducir correo: ")
    contraseña = getpass.getpass("Introducir contraseña: ")
    bd = BaseDeDatos()
    usuario = bd.find_data(correo)
    if usuario is None:
        raise Excepcion("El usuario no existe")
    salt = usuario["Salt"]
    key = usuario["Contraseña_derivada"]
    # verify
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=480000,
    )
    if (kdf.verify(contraseña.encode(), key.encode())) is not None:
        raise Excepcion("Fallo en el inicio de sesion")
    print("Inicio de sesion correcto")


while True:
    print("¡Bienvenido a Hailo")
    a = input("¿Tienes ya una cuenta? (S/N)")
    if a == "S":
        InicioSesion()
        break
    elif a == "N":
        Registro()
        break


