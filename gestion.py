from base_conductores import BaseDeConductores
from base_de_pasajeros import BaseDePasajeros
from comunicacion import Comunicacion
import time
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import tkinter
from tkinter import *
    
class Gestion:
    def __init__(self):
        pass
    
    def Contactar(self, origen, destino, conductor, conductores_ruta, correo_usuario, nombre, ventana_conductor, ventana_reserva ):
        id_c = None
        ventana_error = tkinter.Tk()
        ventana_error.title("Error")
        ventana_error.geometry("300x150")
        ventana_error.config(bg='#ADAFE1')
        ventana_error.resizable(False, False)
        for item in conductores_ruta:
            if item["nombre"].lower() == conductor:
                id_c = item["id"]
        if not id_c:
            error = tkinter.Label(ventana_error, text = "No existe ese conductor", font=("Rockwell Nova Bold", 12), fg= '#2b0d48',  bg='white')
            error.pack(fill = tkinter.BOTH, pady = 20)
            button_aceptar = Button(ventana_error, text="Aceptar", command= ventana_error.destroy, font=("Segoe UI", 10))
            button_aceptar.pack(pady= 10)
            ventana_error.mainloop() 
            return
        
        path = os.path.dirname(__file__) + "/conductores/" + str(id_c) + "/pasajeros.json"
        pasajeros = BaseDePasajeros()
        pasajeros.FILE_PATH = path
        pasajeros.load_store()
        lista = pasajeros.find_data_correo(correo_usuario)
        if len(lista) != 0:
            label_mensaje = Label(ventana_error, text = "Ya has reservado este viaje", font=("Rockwell Nova Bold", 12), fg= '#2b0d48',  bg='#ADAFE1')
            label_mensaje.pack(fill = tkinter.BOTH, pady = 20)
            button_aceptar = Button(ventana_error, text="Aceptar", command= ventana_error.destroy, font=("Segoe UI", 10))
            button_aceptar.pack(pady= 10)
            ventana_error.mainloop()
            return

        #Se llama a la clase comunicación
        conversacion = Comunicacion(conductor, id_c, correo_usuario, nombre, origen, destino)
        label_mensaje = Label(ventana_error, text = "Se ha enviado un mensaje al conductor\n" + conductor +" con tu petición de viaje. \n En breve se pondrá en contacto contigo", font=("Rockwell Nova Bold", 10), fg= '#2b0d48',  bg='#ADAFE1')
        label_mensaje.pack(fill = tkinter.BOTH, pady = 15)
        button_aceptar = Button(ventana_error, text="Aceptar", command= lambda: [ventana_conductor.destroy(), ventana_reserva.destroy(), ventana_error.destroy(), conversacion.enviar_mensaje()], font=("Segoe UI", 10))
        button_aceptar.pack(pady= 10)
        ventana_error.mainloop()
        #time.sleep(5)   
        return 
    #def cerrarVentanas(self, ventana1, ventana2, )
    def Buscar(self,origen, destino, correo_usuario, nombre, ventana_reserva):
        conductores = BaseDeConductores()
        conductores.load_store()
        conductores_ruta = conductores.find_data_ruta(origen, destino)
        ventana_error = tkinter.Tk()
        ventana_error.title("Error")
        ventana_error.geometry("300x150")
        ventana_error.config(bg='#ADAFE1')
        ventana_error.resizable(False, False)
        if len(conductores_ruta) == 0:
            #Si no hay conductores se solicita un viaje distinto
            error = tkinter.Label(ventana_error, text = "No hay conductores disponibles \n para tu viaje.\n", font=("Rockwell Nova Bold", 12), fg= '#2b0d48',  bg='white')
            error.pack(fill = tkinter.BOTH, pady = 20)
            button_aceptar = Button(ventana_error, text="Aceptar", command= ventana_error.destroy, font=("Segoe UI", 10))
            button_aceptar.pack(pady= 10)
            ventana_error.mainloop() 
            return
        ventana_error.destroy()
        ventana_conductores = tkinter.Tk()
        ventana_conductores.title("Conductores disponibles")
        ventana_conductores.geometry("550x650+50+50")
        ventana_conductores.config(bg='#ADAFE1')
        ventana_conductores.resizable(False, False)
        label_disponibles = tkinter.Label(ventana_conductores, text = "Conductores \n disponibles", font=("Rockwell Nova Extra Bold", 25), fg= '#2b0d48')      #Se muestran todos los viajes
        label_disponibles.pack(fill = tkinter.X, pady=10)
        for item in conductores_ruta:
            label_conductor = tkinter.Label(ventana_conductores, text = "Conductor: " + item["nombre"] + ".     Plazas libres: " + str(item["contador"])+ ".    Consumo: "+
                str(item["consumo"]), font=("Rockwell Nova Bold", 10),fg= '#2b0d48',  bg='#ADAFE1')
            label_conductor.pack(pady = 10, padx= 5)
        label_contactar = tkinter.Label(ventana_conductores, text = "¿Con cuál de ellos quieres contactar? ", font=("Rockwell Nova Bold", 12),fg= '#2b0d48',  bg='#ADAFE1')
        label_requisitos = tkinter.Label(ventana_conductores, text = "Introduce el nombre completo", font=("Segoe UI", 10), fg= '#2b0d48', bg='#ADAFE1')
        label_contactar.pack(pady= 10)

        entrada_conductor = Entry(ventana_conductores)
        entrada_conductor.pack(fill = tkinter.BOTH, pady = 10, padx= 70, ipady= 5)

        boton = tkinter.Button(ventana_conductores, text = "Contactar", command= lambda: self.Contactar(origen, destino, entrada_conductor.get().lower(), conductores_ruta, correo_usuario, nombre, ventana_conductores, ventana_reserva))
        boton.pack(pady= 10) 
        ventana_conductores.mainloop()       


    def reservar(self, correo_usuario, nombre, ventana_cuenta = None):
        """
        Función para rerservar un viaje
        """
        if ventana_cuenta is not None:
            ventana_cuenta.destroy()
        ventana_reservar = tkinter.Tk()
        ventana_reservar.title("Reservar")
        ventana_reservar.geometry("550x800+50+0")
        ventana_reservar.resizable(False, False)
        ventana_reservar.config(bg='#ADAFE1')

        label_reservar = tkinter.Label(ventana_reservar, text = "Reservar", font=("Rockwell Nova Extra Bold", 25), fg= '#2b0d48')      #Se muestran todos los viajes
        label_reservar.pack(fill = tkinter.X, pady=10)

        conductores = BaseDeConductores()
        conductores.load_store()
        label_disponibles = tkinter.Label(ventana_reservar, text = "Estos son los viajes disponibles", font=("Rockwell Nova Bold", 12),fg= '#2b0d48',  bg='#ADAFE1')
        label_disponibles.pack(padx= 5)
        lista = []
        for item in conductores._data_list:
            if item["ruta_origen"]+item["ruta_destino"] not in lista:
                if item["contador"] != 0:
                    label_viaje = tkinter.Label(ventana_reservar, text = "Origen: " + item["ruta_origen"] +"            Destino: " + item["ruta_destino"], font=("Segoe UI", 10), fg= '#2b0d48', bg='#ADAFE1')
                    label_viaje.pack(padx= 5)
                    lista.append(item["ruta_origen"]+item["ruta_destino"])
                
        label_origen = tkinter.Label(ventana_reservar, text = "¿Dónde quieres empezar tu viaje?", font=("Rockwell Nova Bold", 10),fg= '#2b0d48',  bg='#ADAFE1')
        label_origen.pack(pady= 15)
        label_sorigen = tkinter.Label(ventana_reservar, text = "Escribe un origen", font=("Segoe UI", 10), fg= '#2b0d48', bg='#ADAFE1')
        label_viaje.pack(padx= 5)
        label_sorigen.pack(padx= 5)
        entrada_origen = Entry(ventana_reservar)
        entrada_origen.pack(fill = tkinter.BOTH, pady = 10, padx= 70, ipady= 5)

        label_destino = tkinter.Label(ventana_reservar, text = "¿A dónde quieres ir?", font=("Rockwell Nova Bold", 10),fg= '#2b0d48',  bg='#ADAFE1')
        label_destino.pack(pady= 10)
        label_sdestino = tkinter.Label(ventana_reservar, text = "Escribe un destino", font=("Segoe UI", 10), fg= '#2b0d48', bg='#ADAFE1')
        label_sdestino.pack()
        entrada_destino = Entry(ventana_reservar)
        entrada_destino.pack(fill = tkinter.BOTH, pady = 10, padx= 70, ipady= 5)

        button_buscar = Button(ventana_reservar, text="Buscar", command= lambda: self.Buscar(entrada_origen.get().lower(), entrada_destino.get().lower(), correo_usuario, nombre, ventana_reservar), font=("Segoe UI", 10))
        button_volver = Button(ventana_reservar, text="Volver", command= ventana_reservar.destroy, font=("Segoe UI", 10))
        button_volver.pack(side="left", pady= 10, padx= 150)
        button_buscar.pack(side="left",pady = 10)
        ventana_reservar.mainloop()
        #Se buscan conductores que realicen ese viaje
        

    def ver_viajes(self, data_list, correo_usuario):
        """
        Función para mostrarle los viajes al usuario
        """
        ventana_viajes = tkinter.Tk()
        ventana_viajes.title("Tus viajes")
        ventana_viajes.geometry("550x800+50+0")
        ventana_viajes.resizable(False, False)
        ventana_viajes.config(bg='#ADAFE1')
        #Se descifra la matrícula
        path = os.path.dirname(__file__) + "/usuarios/" + correo_usuario + "/key.pem"
        with open(path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
            )
        label_viajes = tkinter.Label(ventana_viajes, text = "Estos son tus viajes", font=("Rockwell Nova Extra Bold", 25), fg= '#2b0d48')      #Se muestran todos los viajes
        label_viajes.pack(fill = tkinter.X, pady=10)
        i = 1
        for item in data_list:
            matricula_cifrada = item["Matricula"]
            matricula = private_key.decrypt(
                matricula_cifrada.encode('latin-1'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            lviaje = tkinter.Label(ventana_viajes, text = "Viaje: " + str(i) + "\n Origen: " + item["Origen"] + "\nDestino: " + item["Destino"] + "\n Conductor: " + item["Conductor"] +"\n Matricula: " + matricula.decode('latin-1') +"\n", font=("Rockwell Nova Bold", 12),fg= '#2b0d48',  bg='#ADAFE1')
            lviaje.pack(pady = 10, padx= 5)
            i+=1
        button_volver = Button(ventana_viajes, text="Volver", command= ventana_viajes.destroy, font=("Segoe UI", 10))
        button_volver.pack(pady = 10)
            #print(i)
            #print(" Origen:", item["Origen"],"\n", "Destino:", item["Destino"],"\n", "Conductor:", item["Conductor"],"\n", "Matricula:", matricula.decode('latin-1'),"\n")
           
        ventana_viajes.mainloop()
        #print("¡Esperamos que disfrutes de tus viajes!")