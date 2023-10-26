import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from Datos.base_usuarios import BaseDeUsuarios
from gestion import Gestion
from excepciones import Excepcion
from Atributos.Validaciones import ValidarCampos
import getpass
import random
from Claves.claves import Claves
import json

def Registro():
    validaciones = ValidarCampos()
    nombre = input("Introducir nombre completo: ")
    correo = input("Introducir correo: ")
    res_correo = validaciones.ComprobarCorreo(correo)

    while not res_correo:
        print("El correo no es valido")
        correo = input("Vuelve a introducir tu correo: ")
        res_correo = validaciones.ComprobarCorreo(correo)
    
    telefono = input("Introducir telefono: ")
    res_telefono = validaciones.ComprobarTelefono(telefono)
    
    while not res_telefono:
        print("El teléfono no es valido")
        telefono = input("Vuelve a introducir tu teléfono: ")
        res_telefono= validaciones.ComprobarTelefono(telefono)
    
    contrasenia = getpass.getpass("Introducir contraseña: ")
    res_contrasenia = validaciones.ComprobarConstrasenia(contrasenia)
    validaciones.ValidarContrasenia(res_contrasenia)
    contrasenia_2 = getpass.getpass("Repite la contraseña: ")

    while contrasenia != contrasenia_2:
        print("Las contraseñas no coinciden")
        contrasenia = getpass.getpass("Vuelve a introducir contraseña: ")
        res_contrasenia = validaciones.ComprobarConstrasenia(contrasenia)
        validaciones.ValidarContrasenia(res_contrasenia)
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
        nombre, correo = InicioSesion()
        return nombre, correo

    
    nuevo_usuario={"Nombre": nombre, "Correo": correo, "Telefono": telefono, "Contrasenia_derivada": key.decode('latin-1'), "Salt": salt.decode('latin-1')}
    bd.add_item(nuevo_usuario)
    path = os.path.dirname(__file__) + "/usuarios/" + correo + "/key.pem"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Claves(path, correo).CrearClavePrivada()

    return nombre, correo

def InicioSesion():
    correo = input("Introducir correo: ")
    contrasenia = getpass.getpass("Introducir contraseña: ")
    bd = BaseDeUsuarios()
    usuario = bd.find_data(correo)
    if usuario is None:
        print("El usuario no existe. Regístrate para poder usar la aplicación")
        print("----------------------Registro de usuarios----------------------")
        
        return Registro()
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
            salt=salt,
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

i = 0
print("¡Bienvenido a Hailo")                            #Al abrir la aplicación puedes registrarte o iniciar sesión
while True:                                             #Si ya tienes una cuenta, puedes iniciar sesión
    if i==0:                                            #Si no tienes una cuenta, puedes registrarte                                                      
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
path =  os.path.dirname(__file__) + "/usuarios/" + correo_usuario + "/viajes.json"
reservas = Gestion()
try: 
    with open(path, "r", encoding="utf-8", newline="") as file:
        data_list = json.load(file)
        respuesta = input("Quieres reservar un nuevo viaje (R) o ver tus viajes ya reservados (V)").lower()
        if respuesta == "r":
            reservas.reservar(correo_usuario, nombre)
        elif respuesta == "v":
            reservas.ver_viajes(data_list, correo_usuario)
except FileNotFoundError:
    print("¡Reserva tu primer viaje!")
    reservas.reservar(correo_usuario, nombre)
