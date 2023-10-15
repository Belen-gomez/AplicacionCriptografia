"""
1. iniciar sesion
    a. Si no tienes cuenta, registrarse. Guardar la contraseña en una base de datos con el correo y el salt

"""

import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base_usuarios import BaseDeUsuarios
from base_conductores import BaseDeConductores
from excepciones import Excepcion
import getpass
import re
import base64
from conductor import Conductor
import random
from comunicacion import Comunicacion
import time


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
        contraseña = getpass.getpass("Vuelve a introducir contraseña: ")
        contraseña_2 = getpass.getpass("Repite la contraseña: ")

    # Guardar la contraseña en una base de datos con el correo y el salt
    salt = os.urandom(16)
    # derive
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = kdf.derive(bytes(contraseña.encode("utf-8")))
    # verify
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
   
    if (kdf.verify(contraseña.encode("utf-8"), key)) is not None:
        raise Excepcion("Fallo en el registro")
    
    bd = BaseDeUsuarios()
    if bd.find_data(correo) is not None:
        print("El usuario ya existe. Inicia sesion con tu cuenta")
        InicioSesion()
    
    nuevo_usuario={"Nombre": nombre, "Correo": correo, "Contrasenia_derivada": key.decode('latin-1'), "Salt": salt.decode('latin-1')}
    bd.add_item(nuevo_usuario)

    return nombre

def InicioSesion():
    print("Inicio de sesion")
    correo = input("Introducir correo: ")
    contraseña = getpass.getpass("Introducir contraseña: ")
    bd = BaseDeUsuarios()
    usuario = bd.find_data(correo)
    if usuario is None:
        raise Excepcion("El usuario no existe")
    salt = usuario["Salt"]
    key = usuario["Contrasenia_derivada"]
    # verify
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode('latin-1'),
        iterations=480000,
    )
    if (kdf.verify(bytes(contraseña.encode("latin-1")), key.encode('latin-1'))) is not None:
        raise Excepcion("Fallo en el inicio de sesion")
    print("Inicio de sesion correcto")

    return usuario["Nombre"]





try:
    os.remove("/DATOS/BELÉN/3º UNI/Criptografía/Practica_1/Criptografia/conductores.json")
except:
    pass

conductores = BaseDeConductores()

for i in range(1, random.randint(1, 25)):
    conductor = Conductor(i)
    conductores.add_item(conductor.__dict__)

while True:
    print("¡Bienvenido a Hailo")
    a = input("¿Tienes ya una cuenta? (S/N)")
    if a == "S":
        nombre = InicioSesion()
        break
    elif a == "N":
        nombre = Registro()
        break

print("¡Bienvenido a Hailo", nombre, "!")
origen = input("¿Dónde quieres empezar tu viaje?").lower()
destino = input("¿A dónde quieres ir?").lower()

conductores = BaseDeConductores()

conductores_ruta = conductores.find_data_ruta(origen, destino)

for item in conductores_ruta:
    print("El conductor", item["nombre"], "realiza tu mismo viaje. Le quedan ", item["contador"], "plaza(s) libre(s) y su coche consume",
           item["consumo"], "litros por cada 100 km")

contactar = input("¿Quieres contactar con alguno de estos conductores? (S/N)").lower()
if contactar == "s":
    conductor = input("¿Con cuál de ellos quieres contactar? (Introduce su nombre completo)").lower()

    print("Se ha enviado un mensaje al conductor", conductor, "con tu petición de viaje. En breve se pondrá en contacto contigo")
    time.sleep(5)
    conversacion = Comunicacion(conductor, nombre)
    conversacion.enviar_mensaje()


else:
    print("Lamentamos que no hayas encontrado un conductor para tu viaje. ¡Vuelve pronto!")



