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

contador = 0

def ComprobarConstraseña(correo, contrasenia, ventana_inicio):
    bd = BaseDeUsuarios()
    usuario = bd.find_data(correo)
    ventana_error = tkinter.Tk()
    ventana_error.title("Error")
    ventana_error.geometry("300x150")
    ventana_error.config(bg='#ADAFE1')
    ventana_error.resizable(False, False)
    global contador
    if usuario is None:  
        error = tkinter.Label(ventana_error, text = "El usuario no está registrado", font=("Rockwell Nova Bold", 12), fg= '#2b0d48',  bg='white')
        error.pack(fill = tkinter.BOTH, pady = 20) 
        button_registro = Button(ventana_error, text="Ir al registro", command= Registro, font=("Segoe UI", 10))
        button_registro.pack(pady= 10)
        ventana_inicio.destroy()  
        contador = 0                                                    #Si el usuario no está registrado se le redirige al registro
        return
    
    salt = usuario["Salt"]
    key = usuario["Contrasenia_derivada"]

    # Se verifica la contraseña que la contraseña es la misma que la que estaba almacenada.
    #for i in range(2): 
        #Se tienen tres intentos para introducir bien la contraseña                                                                   
    kdf = Scrypt(                            
        salt=salt.encode('latin-1'),
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    try:
        contador += 1
        kdf.verify(bytes(contrasenia.encode("latin-1")), key.encode('latin-1'))
        
    except:  
        if contador == 3:
                error = tkinter.Label(ventana_error, text = "Contraseña incorrecta.\n Has superado el \n numero de intentos", font=("Rockwell Nova Bold", 12), fg= '#2b0d48',  bg='white')
                error.pack(fill = tkinter.BOTH, pady = 10) 
                button_aceptar = Button(ventana_error, text="Aceptar", command= ventana_error.destroy, font=("Segoe UI", 10))
                button_aceptar.pack(pady= 10)
                ventana_inicio.destroy()
                return                                                                              
        error = tkinter.Label(ventana_error, text = "Contraseña incorrecta", font=("Rockwell Nova Bold", 12), fg= '#2b0d48',  bg='white')
        error.pack(fill = tkinter.BOTH, pady = 20) 
        button_aceptar = Button(ventana_error, text="Aceptar", command= ventana_error.destroy, font=("Segoe UI", 10))
        button_aceptar.pack(pady= 10)
        #ventana_error.mainloop()
        return
            #ventana_error.mainloop()
           
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
    ventana_error.destroy()
    Cuenta(usuario["Nombre"], usuario["Correo"], ventana_inicio)


def Validar_campos(nombre, correo, telefono, contrasenia, contrasenia2, ventana_registro):
    validaciones = ValidarCampos()
    ventana_error = tkinter.Tk()
    ventana_error.title("Error")
    ventana_error.geometry("300x150")
    ventana_error.config(bg='#ADAFE1')
    ventana_error.resizable(False, False)
    if not nombre:
        error = tkinter.Label(ventana_error, text = "El nombre no puede estar vacío", font=("Rockwell Nova Bold", 12), fg= '#2b0d48',  bg='white')
        error.pack(fill = tkinter.BOTH, pady = 20)
        button_aceptar = Button(ventana_error, text="Aceptar", command= ventana_error.destroy, font=("Segoe UI", 10))
        button_aceptar.pack(pady= 10)
        ventana_error.mainloop() 
        return
    res_correo = validaciones.ComprobarCorreo(correo)
    if not res_correo:
        error = tkinter.Label(ventana_error, text = "El correo no es valido", font=("Rockwell Nova Bold", 12), fg= '#2b0d48',  bg='white')
        error.pack(fill = tkinter.BOTH, pady = 20)
        button_aceptar = Button(ventana_error, text="Aceptar", command= ventana_error.destroy, font=("Segoe UI", 10))
        button_aceptar.pack(pady= 10)
        ventana_error.mainloop()
        return
    res_telefono = validaciones.ComprobarTelefono(telefono)
    if not res_telefono:
        error = tkinter.Label(ventana_error, text = "El teléfono no es valido", font=("Rockwell Nova Bold", 12), fg= '#2b0d48',  bg='white')
        error.pack(fill = tkinter.BOTH, pady = 20)
        button_aceptar = Button(ventana_error, text="Aceptar", command= ventana_error.destroy, font=("Segoe UI", 10))
        button_aceptar.pack(pady= 10)
        ventana_error.mainloop()
        return
    res_contrasenia = validaciones.ComprobarConstrasenia(contrasenia)
    if not res_contrasenia:
        error = tkinter.Label(ventana_error, text = "La contraseña no es valida", font=("Rockwell Nova Bold", 12), fg= '#2b0d48',  bg='white')
        error.pack(fill = tkinter.BOTH, pady = 20)
        button_aceptar = Button(ventana_error, text="Aceptar", command= ventana_error.destroy, font=("Segoe UI", 10))
        button_aceptar.pack(pady= 10)
        ventana_error.mainloop()
        return
    if contrasenia != contrasenia2:
        error = tkinter.Label(ventana_error, text = "Las contraseñas no coinciden", font=("Rockwell Nova Bold", 12), fg= '#2b0d48',  bg='white')
        error.pack(fill = tkinter.BOTH, pady = 20)
        button_aceptar = Button(ventana_error, text="Aceptar", command= ventana_error.destroy, font=("Segoe UI", 10))
        button_aceptar.pack(pady= 10)
        ventana_error.mainloop()   
        return
    bd = BaseDeUsuarios()
    #Si el usuario ya estaba registrado se le redirige al inico de sesión
    if bd.find_data(correo) is not None:
        error = tkinter.Label(ventana_error, text = "El usuario ya está registrado", font=("Rockwell Nova Bold", 12), fg= '#2b0d48',  bg='white')
        error.pack(fill = tkinter.BOTH, pady = 20) 
        button_registro = Button(ventana_error, text="Ir al inicio de sesion", command= InicioSesion, font=("Segoe UI", 10))
        button_registro.pack(pady= 10)
        ventana_registro.destroy()
        return #nombre, correo
    ventana_error.destroy()
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

    #se crea una clave privada para el usuario y se almacena de forma segura. La clave pública se guarda en una base de datos
    path = os.path.dirname(__file__) + "/usuarios/" + correo
    os.makedirs(path, exist_ok=True)
    Claves(path, correo, telefono).CrearClavePrivada()
    #se guarda el usuario en la base de datos
    nuevo_usuario={"Nombre": nombre, "Correo": correo, "Telefono": telefono, "Contrasenia_derivada": key.decode('latin-1'), "Salt": salt.decode('latin-1')}
    bd.add_item(nuevo_usuario)
    Cuenta(nombre, correo, ventana_registro)
    return

def Registro():
    """
    Función que registra a un usuario en la aplicación
    """ 
               
    ventana_registro = tkinter.Tk()
    ventana_registro.geometry("550x650+50+50")
    ventana_registro.resizable(False, False)
    ventana_registro.config(bg='#ADAFE1')
    titulo = tkinter.Label(ventana_registro, text = "Registro", font=("Rockwell Nova Extra Bold", 25), fg= '#2b0d48')  
    titulo.pack(fill = tkinter.X, pady = 20)
    ventana_registro.title("Registro")
    
    label_nombre = tkinter.Label(ventana_registro, text = "Nombre completo: ", font=("Rockwell Nova Bold", 15), fg= '#2b0d48',  bg='#ADAFE1') 
    label_correo = tkinter.Label(ventana_registro, text = "Correo: ", font=("Rockwell Nova Bold", 15), fg= '#2b0d48',  bg='#ADAFE1') 
    label_telefono = tkinter.Label(ventana_registro, text = "Telefono: ", font=("Rockwell Nova Bold", 15), fg= '#2b0d48',  bg='#ADAFE1') 
    label_contrasenia1 = tkinter.Label(ventana_registro, text = "Contraseña: ", font=("Rockwell Nova Bold", 15), fg= '#2b0d48',  bg='#ADAFE1') 
    label_requisitos = tkinter.Label(ventana_registro, text = "Mínimo 8 caracteres, una mayúscula, una minúscula y un número", font=("Segoe UI", 10), fg= '#2b0d48', bg='#ADAFE1')
    label_contrasenia2 = tkinter.Label(ventana_registro, text = "Repite la contraseña: ", font=("Rockwell Nova Bold", 15), fg= '#2b0d48',  bg='#ADAFE1') 
    
    entrada_nombre = Entry(ventana_registro)
    entrada_correo = Entry(ventana_registro)
    entrada_telefono = Entry(ventana_registro) 
    entrada_contrasenia1 = Entry(ventana_registro, show="*") 
    entrada_contrasenia2 = Entry(ventana_registro, show="*") 
    
    label_nombre.pack(fill = tkinter.BOTH, pady = 3)
    entrada_nombre.pack(fill = tkinter.BOTH, pady = 10, padx= 70, ipady= 5)

    label_correo.pack(fill = tkinter.BOTH, pady = 3)
    entrada_correo.pack(fill = tkinter.BOTH, pady = 10, padx= 70, ipady= 5)

    label_telefono.pack(fill = tkinter.BOTH, pady =3)
    entrada_telefono.pack(fill = tkinter.BOTH, pady = 10, padx= 70, ipady= 5)

    label_contrasenia1.pack(fill = tkinter.BOTH, pady = 3)
    label_requisitos.pack(fill = tkinter.BOTH, pady = 3)
    entrada_contrasenia1.pack(fill = tkinter.BOTH, pady = 10, padx= 70, ipady= 5)

    label_contrasenia2.pack(fill = tkinter.BOTH, pady = 3)
    entrada_contrasenia2.pack(fill = tkinter.BOTH, pady = 10, padx= 70, ipady= 5)
    
    button_aceptar = Button(ventana_registro, text="Aceptar", command= lambda: Validar_campos(entrada_nombre.get(), entrada_correo.get(), entrada_telefono.get(), entrada_contrasenia1.get(), entrada_contrasenia2.get(), ventana_registro), font=("Segoe UI", 10))
    button_volver = Button(ventana_registro, text="Volver", command= ventana_registro.destroy, font=("Segoe UI", 10))
    button_volver.pack(side="left", pady= 10, padx= 150)
    button_aceptar.pack(side="left",pady = 10)
    ventana_registro.mainloop()
    return #nombre, correo

def InicioSesion():
    """
    Función para iniciar sesión
    """
    ventana_inicio = tkinter.Tk()
    ventana_inicio.geometry("550x650+50+50")
    ventana_inicio.resizable(False, False)
    ventana_inicio.config(bg='#ADAFE1')
    titulo = tkinter.Label(ventana_inicio, text = "Incio de sesión", font=("Rockwell Nova Extra Bold", 25), fg= '#2b0d48')  
    titulo.pack(fill = tkinter.X, pady = 20)
    ventana_inicio.title("Inicio")

    label_correo = tkinter.Label(ventana_inicio, text = "Correo: ", font=("Rockwell Nova Bold", 15), fg= '#2b0d48',  bg='#ADAFE1') 
    label_contrasenia1 = tkinter.Label(ventana_inicio, text = "Contraseña: ", font=("Rockwell Nova Bold", 15), fg= '#2b0d48',  bg='#ADAFE1') 
    entrada_correo = Entry(ventana_inicio)
    entrada_contrasenia1 = Entry(ventana_inicio, show="*")
    label_correo.pack(fill = tkinter.BOTH, pady = 3)
    entrada_correo.pack(fill = tkinter.BOTH, pady = 10, padx= 70, ipady= 5)
    label_contrasenia1.pack(fill = tkinter.BOTH, pady = 3)
    entrada_contrasenia1.pack(fill = tkinter.BOTH, pady = 10, padx= 70, ipady= 5)
    button_aceptar = Button(ventana_inicio, text="Aceptar", command= lambda: ComprobarConstraseña(entrada_correo.get(), entrada_contrasenia1.get(), ventana_inicio), font=("Segoe UI", 10))
    button_volver = Button(ventana_inicio, text="Volver", command= ventana_inicio.destroy, font=("Segoe UI", 10))
    button_volver.pack(pady= 10, padx= 150)
    button_aceptar.pack(pady = 10)
    ventana_inicio.mainloop()
    
    return #usuario["Nombre"], usuario["Correo"]

def Cuenta(nombre, correo_usuario, ventana_cerrar):
    ventana_cerrar.destroy()
    ventana_cuenta = tkinter.Tk()
    ventana_cuenta.title("Tu cuenta")
    ventana_cuenta.geometry("550x650+50+50")
    ventana_cuenta.resizable(False, False)
    ventana_cuenta.config(bg='#ADAFE1')
    bienvenido = tkinter.Label(ventana_cuenta, text = "Bienvenido "+ nombre, font=("Rockwell Nova Extra Bold", 25), fg= '#2b0d48') 
    bienvenido.pack(fill = tkinter.X, pady = 20) 
    path =  os.path.dirname(__file__) + "/usuarios/" + correo_usuario + "/viajes.json"
    reservas = Gestion()
    try: 
    #Si el usuario tiene viajes, puede reservar o ver sus viajes
        with open(path, "r", encoding="utf-8", newline="") as file:
            data_list = json.load(file)
            label_elegir = tkinter.Label(ventana_cuenta, text = "¿Quieres reservar un nuevo viaje \n o ver tus viajes ya reservados? ", font=("Rockwell Nova Bold", 15), fg= '#2b0d48',  bg='#ADAFE1') 
            button_reservar = Button(ventana_cuenta, text="Reservar viaje", command= lambda: reservas.reservar(correo_usuario, nombre, ventana_cuenta), font=("Segoe UI", 10))
            button_ver = Button(ventana_cuenta, text="Ver viajes", command= lambda: reservas.ver_viajes(data_list, correo_usuario), font=("Segoe UI", 10))
            label_elegir.pack(fill = tkinter.BOTH, pady = 3)
            button_reservar.pack(pady= 10, padx= 150)
            button_ver.pack(pady = 10)
            ventana_cuenta.mainloop()
    except:
        #sino, solo puede reservar
        ventana_cuenta.destroy()
        reservas.reservar(correo_usuario, nombre)
        
    return

ventana = tkinter.Tk()
ventana.title("Hailo")
ventana.geometry("550x650+50+50")
ventana.resizable(False, False)
ventana.config(bg='#ADAFE1')
bienvenido = tkinter.Label(ventana, text = "Bienvenido a Hailo", font=("Rockwell Nova Extra Bold", 25), fg= '#2b0d48')  
eslogan = tkinter.Label(ventana, text = "¿Viajamos juntos?", font=("Rockwell Nova Extra Bold", 25), fg= '#2b0d48',  bg='#ADAFE1')  
img = Image.open( os.path.dirname(__file__) +"/logo.png")
img = img.resize((200, 200), Image.LANCZOS)
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

''' i = 0                                                         #Al abrir la aplicación puedes registrarte o iniciar sesión
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
    reservas.reservar(correo_usuario, nombre) '''

