from tkinter import *
import os
import tkinter
from PIL import ImageTk, Image
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from base_usuarios import BaseDeUsuarios
from gestion import Gestion
from excepciones import Excepcion
from Atributos.Validaciones import ValidarCampos
import getpass
import random
from claves import Claves
import json
import sys


def Registro():
    """
    Función que registra a un usuario en la aplicación
    """
    ventana_registro = tkinter.Tk()
    ventana_registro.geometry("550x650")
    ventana_registro.resizable(False, False)
    ventana_registro.config(bg='#ADAFE1')
    titulo = tkinter.Label(ventana_registro, text = "Registro", font=("Rockwell Nova Extra Bold", 25), fg= '#2b0d48')  
    titulo.pack(fill = tkinter.X, pady = 20)
    ventana_registro.title("Registro")
    label_nombre = tkinter.Label(ventana_registro, text = "Nombre completo: ", font=("Rockwell Nova Bold", 20), fg= '#2b0d48',  bg='#ADAFE1') 
    entrada = Entry(ventana_registro) 
    validaciones = ValidarCampos()
    label_nombre.pack(fill = tkinter.BOTH, pady = 10)
    entrada.pack(fill = tkinter.BOTH, pady = 10)

    nombre = input("Introducir nombre completo: ")
    correo = input("Introducir correo: ")
    res_correo = validaciones.ComprobarCorreo(correo)

    #para cada campo se comprueba que sea válido. Si no lo es, se vuelve a pedir
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

    #La contraseña se pide dos veces y se comprueba que coincide
    while contrasenia != contrasenia_2:                                           
        print("Las contraseñas no coinciden")
        contrasenia = getpass.getpass("Vuelve a introducir contraseña: ")
        res_contrasenia = validaciones.ComprobarConstrasenia(contrasenia)
        validaciones.ValidarContrasenia(res_contrasenia)
        contrasenia_2 = getpass.getpass("Repite la contraseña: ")

    # Guardar la contraseña derivada en una base de datos con el correo y el salt
    salt = os.urandom(16)
    # Se deriva la contraseña
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    key = kdf.derive(bytes(contrasenia.encode("utf-8")))

    bd = BaseDeUsuarios()
    #Si el usuario ya estaba registrado se le redirige al inico de sesión
    if bd.find_data(correo) is not None:
        print("El usuario ya existe. Inicia sesion con tu cuenta")
        print("----------------------Incio de sesion----------------------")
        nombre, correo = InicioSesion()
        return nombre, correo

   
   
    #se crea una clave privada para el usuario y se almacena de forma segura. La clave pública se guarda en una base de datos
    print("Adios")
    path = os.path.dirname(__file__) + "/usuarios/" + correo
    os.makedirs(path, exist_ok=True)
    print("hola")
    Claves(path, correo, telefono).CrearClavePrivada()
    #se guarda el usuario en la base de datos
    nuevo_usuario={"Nombre": nombre, "Correo": correo, "Telefono": telefono, "Contrasenia_derivada": key.decode('latin-1'), "Salt": salt.decode('latin-1')}
    bd.add_item(nuevo_usuario)
    ventana_registro.mainloop()
    return nombre, correo

def InicioSesion():
    """
    Función para iniciar sesión
    """
    correo = input("Introducir correo: ")
    contrasenia = getpass.getpass("Introducir contraseña: ")
    bd = BaseDeUsuarios()
    usuario = bd.find_data(correo)
    if usuario is None:                                                                   #Si el usuario no está registrado se le redirige al registro
        print("El usuario no existe. Regístrate para poder usar la aplicación")
        print("----------------------Registro de usuarios----------------------")
        
        return Registro()
    
    salt = usuario["Salt"]
    key = usuario["Contrasenia_derivada"]

    # Se verifica la contraseña que la contraseña es la misma que la que estaba almacenada.
    for i in range(2): 
        #Se tienen tres intentos para introducir bien la contraseña                                                                   
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
    #El 50% de las veces que se inicia sesión se cambia el token de la contraseña
    cambio_token = random.randint(1, 2)
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


ventana = tkinter.Tk()
ventana.title("Hailo")
ventana.geometry("550x650")
ventana.resizable(False, False)
ventana.config(bg='#ADAFE1')
bienvenido = tkinter.Label(ventana, text = "Bienvenido a Hailo", font=("Rockwell Nova Extra Bold", 25), fg= '#2b0d48')  
eslogan = tkinter.Label(ventana, text = "¿Viajamos juntos?", font=("Rockwell Nova Extra Bold", 25), fg= '#2b0d48',  bg='#ADAFE1')  
img = Image.open( os.path.dirname(__file__) +"/logo.png")
img = img.resize((200, 200), Image.ANTIALIAS)
img = ImageTk.PhotoImage(img)
label = tkinter.Label(ventana, image=img, bg='#ADAFE1')
bienvenido.pack(fill = tkinter.X, pady = 20)
label.pack(fill = tkinter.BOTH)
eslogan.pack(fill = tkinter.BOTH, pady = 40)
inicio = tkinter.Label(ventana, text = "¿Tienes ya una cuenta?", font=("Segoe UI", 15), fg= '#2b0d48', bg='#ADAFE1')  
registro = tkinter.Label(ventana, text = "¿Todavía no has empezado esta aventura?", font=("Segoe UI", 15), fg= '#2b0d48', bg='#ADAFE1')  
button_inicio = Button(ventana, text="Inicio de sesion", command= InicioSesion, font=("Segoe UI", 10))
button_registro = Button(ventana, text="Registro", command= Registro, font=("Segoe UI", 10))
inicio.pack(fill = tkinter.BOTH, pady = 10)
button_inicio.pack(pady = 10)
registro.pack(fill = tkinter.BOTH, pady = 10)
button_registro.pack(pady = 10)
ventana.protocol("WM_DELETE_WINDOW", ventana.destroy) 
ventana.mainloop()

i = 0                                                         #Al abrir la aplicación puedes registrarte o iniciar sesión
while True:                                             #Si ya tienes una cuenta, puedes iniciar sesión
    if i==0:                                            #Si no tienes una cuenta, puedes registrarte                                                      
        a = input("¿Tienes ya una cuenta? (S/N) ").lower()
    else:
        a = input("¿Tienes ya una cuenta? Responde 'S' si tienes una cuenta o 'N' si no la tienes ").lower()

    if a == "s":
        os.system("cls")
        print("----------------------Incio de sesion----------------------")
        nombre, correo_usuario = InicioSesion()
        break
    elif a == "n":
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
    #Si el usuario tiene viajes, puede reservar o ver sus viajes
    with open(path, "r", encoding="utf-8", newline="") as file:
        data_list = json.load(file)
        respuesta = input("Quieres reservar un nuevo viaje (R) o ver tus viajes ya reservados (V)").lower()
        while respuesta != "r" and respuesta != "v":
            respuesta = input("Quieres reservar un nuevo viaje (R) o ver tus viajes ya reservados (V)").lower()
        if respuesta == "r":
            reservas.reservar(correo_usuario, nombre)
        else:
            reservas.ver_viajes(data_list, correo_usuario)

except FileNotFoundError:
    #sino, solo puede reservar
    print("¡Reserva tu primer viaje!")
    reservas.reservar(correo_usuario, nombre)

