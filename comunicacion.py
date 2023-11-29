from base_conductores import BaseDeConductores
import os
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives import padding
import random
import string
from usuarios.usuario import Usuario
from conductores.conductor import Conductor
from base_de_pasajeros import BaseDePasajeros
import json
from base_viajes import BaseDeViajes
import tkinter
from tkinter import *
from tkinter import scrolledtext

class Comunicacion:
    
    def __init__(self, nombre_conductor, id, correo, nombre_usuario, origen, destino):
         #Creamos el conductor y el usuario de la comunciación
         self.usuario = self.crear_usuario(correo, nombre_usuario)
         self.conductor = self.crear_conductor(nombre_conductor, id)
         self.origen = origen
         self.destino = destino

    def crear_usuario(self, correo, nombre_usuario):
        usuario = Usuario(correo, nombre_usuario)
        return usuario
    
    def crear_conductor(self, nombre_conductor, id):
        conductor=Conductor(nombre_conductor, id)
        return conductor
    
    def send_msg(self, msg_entry, chat_area, send_button):
        user_msg = msg_entry.get()
        chat_area.insert(tkinter.END, "Usuario: " + user_msg + "\n", 'usuario')
        msg_entry.delete(0, tkinter.END)
        if "Seguro que nos lo pasaremos genial!" not in chat_area.get('1.0', tkinter.END):
            chat_area.insert(tkinter.END, "Conductor: Seguro que nos lo pasaremos genial!\n", 'conductor')
        elif "Por favor, introduce la dirección del punto de encuentro." not in chat_area.get('1.0', tkinter.END):
            chat_area.insert(tkinter.END, "Conductor: Por favor, introduce la dirección del punto de encuentro.\n", 'conductor')
            
        else:
            direccion_cifrada, sign_direccion, ac_raiz, ac_usuario, usuario = self.usuario.cifrar_direccion(msg_entry.get())
            pasajero = self.conductor.descifrar_direccion(direccion_cifrada, sign_direccion, self.usuario.correo, self.usuario._public_key, ac_raiz, ac_usuario, usuario)
            matricula_cifrada, sign_matricula, ac_raiz, ac_conductor, conductor = self.conductor.cifrar_matricula()
            matricula_cifrada, matricula = self.usuario.descifrar_matricula(matricula_cifrada, sign_matricula, self.conductor._public_key, ac_raiz, ac_conductor, conductor)
            chat_area.insert(tkinter.END, "Conductor: Ahora te voy a enviar mi matricula\n",  'conductor')
            time.sleep(2)
            chat_area.insert(tkinter.END, "Conductor: Esta es mi matrícula" + matricula + "\n", 'conductor')
            conductores = BaseDeConductores()
            conductor_sel = conductores.find_data_id(self.conductor.id)
            conductor_sel["contador"] -= 1

            #Se añade el pasajero a la base de datos del conductor
            path = os.path.dirname(__file__) + "/conductores/" + str(self.conductor.id) + "/pasajeros.json"
            conductores.save_store()
            pasajeros = BaseDePasajeros()
            pasajeros.FILE_PATH = path
            pasajeros.load_store()
            pasajeros.add_item(pasajero)
            pasajeros.save_store()

            #Se añade el viaje a la base del usuario
            viajes = BaseDeViajes()
            path = os.path.dirname(__file__) + "/usuarios/" + self.usuario.correo + "/viajes.json"
            viajes.FILE_PATH = path
            viajes.load_store()
            data_list = {"Origen": self.origen, "Destino": self.destino, "Conductor": self.conductor.nombre, "Matricula": matricula_cifrada.decode('latin-1')}
            viajes.add_item(data_list)
            viajes.save_store()
            chat_area.insert(tkinter.END, "Conductor: Ya estás apuntado para el viaje\n", 'conductor')
            chat_area.insert(tkinter.END, "Conductor: ¡Ya estamos listos para irnos\n!", 'conductor')
            msg_entry.pack_forget()
            send_button.pack_forget()


    def enviar_mensaje(self):
        ac_raiz, ac_conductor, conductor = self.conductor.ObtenerCertificados()
        self.usuario.VerificarCertificados(ac_raiz, ac_conductor, conductor)
        clave_cifrada, iv = self.usuario.cifrado_simetrico(self.conductor._public_key)

        self.conductor.cifrado_simetrico(clave_cifrada, iv)
        window = tkinter.Tk()
        window.geometry("550x650+50+50")
        window.resizable(False, False)
        window.config(bg='#ADAFE1')
        window.title("Chat con Conductor")

        chat_area = scrolledtext.ScrolledText(window, width=50, height=30, bg='#ADAFE1')
        chat_area.pack(pady=10)

        msg_entry = tkinter.Entry(window, width=50)
        msg_entry.pack(pady=10)   

        chat_area.insert(tkinter.END, "Conductor: Hola, ¿cómo estás?\n", 'conductor')
        chat_area.tag_config('conductor', background='white')
        chat_area.tag_config('usuario', background= '#ADAFE1')

        send_button = tkinter.Button(window, text="Enviar", command=lambda:self.send_msg(msg_entry, chat_area, send_button))
        send_button.pack()

        window.mainloop()

       
        #Se pide la dirección al usuario y se cifra con la clave simétrica
        

        #el conductor descifra el mensaje
       
        #print("Ahora te voy a enviar mi matricula")

        #El conductor manda su matrícula cifrada y el usuario la descifra
        
        
        #Se modifica el contandar del conductor
       
        
    