"""
1. iniciar sesion
    a. Si no tienes cuenta, registrarse. Guardar la contraseña en una base de datos con el correo y el salt

"""

import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from base_usuarios import BaseDeUsuarios
from base_conductores import BaseDeConductores
from excepciones import Excepcion
import getpass
import re
import random
from comunicacion import Comunicacion
import time
from claves import Claves
from base_de_pasajeros import BaseDePasajeros


def ComprobarCorreo(correo):
    regex = r"^[a-z0-9]+(\.[a-z0-9]+)*[@](\w+[.])+\w{2,3}$"
    myregex = re.compile(regex)
    res = myregex.fullmatch(correo)
    return res

def ComprobarConstrasenia(contrasenia):
    regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d\W]{8,}$"
    myregex = re.compile(regex)
    res = myregex.fullmatch(contrasenia)
    return res

def ValidarContrasenia(res_contrasenia):
    while not res_contrasenia:
        print("La contraseña no es valida. Debe tener al menos 8 caracteres, una mayuscula, una minuscula y un numero.")
        contrasenia = getpass.getpass("Introduce una nueva contraseña: ")
        res_contrasenia = ComprobarConstrasenia(contrasenia)
    return

def ComprobarTelefono(telefono):
    regex = r"^[67]{1}[0-9]{8}$"
    myregex = re.compile(regex)
    res = myregex.fullmatch(telefono)
    return res

def Registro():
    nombre = input("Introducir nombre completo: ")
    correo = input("Introducir correo: ")
    res_correo = ComprobarCorreo(correo)

    while not res_correo:
        print("El correo no es valido")
        correo = input("Vuelve a introducir tu correo: ")
        res_correo = ComprobarCorreo(correo)
    
    telefono = input("Introducir telefono: ")
    res_telefono = ComprobarTelefono(telefono)
    
    while not res_telefono:
        print("El teléfono no es valido")
        telefono = input("Vuelve a introducir tu teléfono: ")
        res_telefono= ComprobarTelefono(telefono)
    
    contrasenia = getpass.getpass("Introducir contraseña: ")
    res_contrasenia = ComprobarConstrasenia(contrasenia)
    ValidarContrasenia(res_contrasenia)
    contrasenia_2 = getpass.getpass("Repite la contraseña: ")

    while contrasenia != contrasenia_2:
        print("Las contraseñas no coinciden")
        contrasenia = getpass.getpass("Vuelve a introducir contraseña: ")
        res_contrasenia = ComprobarConstrasenia(contrasenia)
        ValidarContrasenia(res_contrasenia)
        contrasenia_2 = getpass.getpass("Repite la contraseña: ")

    # Guardar la contraseña en una base de datos con el correo y el salt
    salt = os.urandom(16)
    # derive
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    key = kdf.derive(bytes(contrasenia.encode("utf-8")))

    bd = BaseDeUsuarios()
    if bd.find_data(correo) is not None:
        print("El usuario ya existe. Inicia sesion con tu cuenta")
        print("----------------------Incio de sesion----------------------")
        InicioSesion()
    
    
    nuevo_usuario={"Nombre": nombre, "Correo": correo, "Telefono": telefono, "Contrasenia_derivada": key.decode('latin-1'), "Salt": salt.decode('latin-1')}
    bd.add_item(nuevo_usuario)
    path = "usuarios/" + correo + "/key.pem"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Claves(path).CrearClavePrivada()

    return nombre, correo

def InicioSesion():
    correo = input("Introducir correo: ")
    contrasenia = getpass.getpass("Introducir contraseña: ")
    bd = BaseDeUsuarios()
    usuario = bd.find_data(correo)
    if usuario is None:
        print("El usuario no existe. Regístrate para poder usar la aplicación")
        print("----------------------Registro de usuarios----------------------")
        Registro()
        return
    salt = usuario["Salt"]
    key = usuario["Contrasenia_derivada"]
    # verify
     
    for i in range(2):
        kdf = Scrypt(
            salt=salt.encode('latin-1'),
            length=32,
            n=2**14,
            r=8,
            p=1,
        )
        try:
            kdf.verify(bytes(contrasenia.encode("latin-1")), key.encode('latin-1'))
            break
        except:
            print("Contraseña incorrecta")
            contrasenia = getpass.getpass("Vuelve a introducir contraseña: ")
            if i == 1:
                raise Excepcion("Contraseña incorrecta. Has superado el numero de intentos")  

    print("Inicio de sesion correcto")
    cambio_token = random.randint(1, 10)
    if cambio_token == 1:
        salt = os.urandom(16)
        # derive
        kdf = Scrypt(
            salt=salt.encode('latin-1'),
            length=32,
            n=2**14,
            r=8,
            p=1,
        )
        key = kdf.derive(bytes(contrasenia.encode("utf-8")))

        usuario["Contrasenia_derivada"] = key.decode('latin-1')
        usuario["Salt"] = salt.decode('latin-1')

        bd.save_store()

    return usuario["Nombre"], usuario["Correo"]


def BuscarConductor(conductores_ruta):
    while len(conductores_ruta) == 0:
        opciones = input("No hay conductores para tu viaje. ¿Quieres probar con otro origen o destino? (S/N) ")
        if opciones == "N":
            print("Lamentamos que no hayas encontrado un conductor para tu viaje. ¡Vuelve pronto!")
            exit()
        elif opciones == "S":
            origen = input("¿Dónde quieres empezar tu viaje? ").lower()
            destino = input("¿A dónde quieres ir? ").lower()
        conductores_ruta = conductores.find_data_ruta(origen, destino)
    return conductores_ruta


''' try:
    os.remove("/DATOS/BELÉN/3º UNI/Criptografía/Practica_1/Criptografia/conductores.json")
except:
    pass

conductores = BaseDeConductores()

for i in range(1, random.randint(1, 25)):
    conductor = GeneradorDatos(i)
    conductores.add_item(conductor.__dict__) '''

i = 0
while True:
    print("¡Bienvenido a Hailo")
    if i==0:
        a = input("¿Tienes ya una cuenta? (S/N) ")
    else:
        a = input("¿Tienes ya una cuenta? Responde 'S' si tienes una cuenta o 'N' si no la tienes ")

    if a == "S":
        os.system("cls")
        print("----------------------Incio de sesion----------------------")
        nombre, correo_usuario = InicioSesion()
        break
    elif a == "N":
        os.system("cls")
        print("----------------------Registro de usuarios----------------------")
        nombre, correo_usuario = Registro()
        break
    i+=1

os.system("cls")
print("¡Bienvenido a Hailo", nombre, "!")
origen = input("¿Dónde quieres empezar tu viaje? ").lower()
destino = input("¿A dónde quieres ir? ").lower()

conductores = BaseDeConductores()

conductores_ruta = conductores.find_data_ruta(origen, destino)
if len(conductores_ruta) == 0:
    conductores_ruta = BuscarConductor(conductores_ruta)

for item in conductores_ruta:
    print("El conductor", item["nombre"], "realiza tu mismo viaje. Le quedan ", item["contador"], "plaza(s) libre(s) y su coche consume",
        item["consumo"], "litros por cada 100 km")

contactar = input("¿Quieres contactar con alguno de estos conductores? (S/N)").lower()
if contactar == "s":
    conductor = input("¿Con cuál de ellos quieres contactar? (Introduce su nombre completo)").lower()
    for item in conductores_ruta:
        if item["nombre"].lower() == conductor:
            id = item["id"]
    
    print("Se ha enviado un mensaje al conductor", conductor, "con tu petición de viaje. En breve se pondrá en contacto contigo")
    time.sleep(5)

    path = "conductores/" + str(id) + "/pasajeros.json"
    pasajeros = BaseDePasajeros()
    pasajeros.FILE_PATH = path
    pasajeros.load_store()
    lista = pasajeros.find_data_correo(correo_usuario)
    if len(lista) != 0:
        print("Ya has contactado con este conductor y has reservado un viaje. ¡Seguro que os lo pasáis genial!")
        exit()

    conversacion = Comunicacion(conductor, id, correo_usuario, nombre)
    conversacion.enviar_mensaje()

else:
    print("Lamentamos que no hayas encontrado un conductor para tu viaje. ¡Vuelve pronto!")



