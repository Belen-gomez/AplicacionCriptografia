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
    
    def Contactar(self, conductor, conductores_ruta):
        id_c = None
        for item in conductores_ruta:
            if item["nombre"].lower() == conductor:
                id_c = item["id"]
        return id_c
    
    def BuscarConductor(self, conductores_ruta):
        conductores = BaseDeConductores()
        while len(conductores_ruta) == 0:
            opciones = input("No se ha encontrado esa información. ¿Quieres probar con otro origen o destino? (S/N) ").lower()
            if opciones == "s":
                origen = input("¿Dónde quieres empezar tu viaje? ").lower()
                destino = input("¿A dónde quieres ir? ").lower()
                conductores_ruta = conductores.find_data_ruta(origen, destino)
            elif opciones == "n":
                print("Lamentamos que no hayas encontrado un conductor para tu viaje. ¡Vuelve pronto!")
                exit()
            else:
                conductores_ruta = {}
        return conductores_ruta, origen, destino

    def reservar(self, correo_usuario, nombre, ventana_cuenta = None):
        """
        Función para rerservar un viaje
        """
        if ventana_cuenta is not None:
            ventana_cuenta.destroy()
        ventana_reservar = tkinter.Tk()
        ventana_reservar.title("Reservar")
        ventana_reservar.geometry("550x750+50+0")
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
                    label_viaje = tkinter.Label(ventana_reservar, text = "Origen: " + item["ruta_origen"] +" Destino: " + item["ruta_destino"], font=("Segoe UI", 10), fg= '#2b0d48', bg='#ADAFE1')
                    label_viaje.pack(padx= 5)
                    lista.append(item["ruta_origen"]+item["ruta_destino"])
                #print("Origen: ", item["ruta_origen"], " - Destino: ", item["ruta_destino"])
            
        #Se pide el viaje
        label_origen = tkinter.Label(ventana_reservar, text = "¿Dónde quieres empezar tu viaje?", font=("Rockwell Nova Bold", 10),fg= '#2b0d48',  bg='#ADAFE1')
        label_origen.pack(pady= 15)
        entrada_origen = Entry(ventana_reservar)
        entrada_origen.pack(fill = tkinter.BOTH, pady = 10, padx= 70, ipady= 5)

        label_destino = tkinter.Label(ventana_reservar, text = "¿A dónde quieres ir?", font=("Rockwell Nova Bold", 10),fg= '#2b0d48',  bg='#ADAFE1')
        label_destino.pack(pady= 10)
        entrada_origen = Entry(ventana_reservar)
        entrada_origen.pack(fill = tkinter.BOTH, pady = 10, padx= 70, ipady= 5)

        button_buscar = Button(ventana_reservar, text="Buscar", command= ventana_reservar.destroy, font=("Segoe UI", 10))
        button_volver = Button(ventana_reservar, text="Volver", command= ventana_reservar.destroy, font=("Segoe UI", 10))
        button_buscar.pack(side="left", pady= 10, padx= 150)
        button_volver.pack(side="left",pady = 10)
        ventana_reservar.mainloop()
        #Se buscan conductores que realicen ese viaje
        conductores_ruta = conductores.find_data_ruta(origen, destino)
        if len(conductores_ruta) == 0:
            #Si no hay conductores se solicita un viaje distinto
            conductores_ruta, origen, destino = self.BuscarConductor(conductores_ruta)

        for item in conductores_ruta:
            print("El conductor", item["nombre"], "realiza tu mismo viaje. Le quedan ", item["contador"], "plaza(s) libre(s) y su coche consume",
                item["consumo"], "litros por cada 100 km")

        #Se muestran los conductores y se permite al usuario elegir
        contactar = input("¿Quieres contactar con alguno de estos conductores? (S/N)").lower()
        while contactar != "s" and contactar != "n":
            contactar = input("¿Quieres contactar con alguno de estos conductores? (S/N)").lower()
            
        if contactar == "s":
            conductor = input("¿Con cuál de ellos quieres contactar? (Introduce su nombre completo)").lower()
            id = self.Contactar(conductor, conductores_ruta)
        
            while not id:
                conductor = input("¿Con cuál de ellos quieres contactar? (Introduce su nombre completo)").lower()
                id = self.Contactar(conductor, conductores_ruta)
                
            print("Se ha enviado un mensaje al conductor", conductor, "con tu petición de viaje. En breve se pondrá en contacto contigo")
            time.sleep(5)

            path = os.path.dirname(__file__) + "/conductores/" + str(id) + "/pasajeros.json"
            pasajeros = BaseDePasajeros()
            pasajeros.FILE_PATH = path
            pasajeros.load_store()
            lista = pasajeros.find_data_correo(correo_usuario)
            if len(lista) != 0:
                #Si ya se ha reservado un viaje con ese conductor se muestra un mensaje
                print("Ya has contactado con este conductor y has reservado un viaje. ¡Seguro que os lo pasáis genial!")
                exit()

            #Se llama a la clase comunicación
            conversacion = Comunicacion(conductor, id, correo_usuario, nombre, origen, destino)
            conversacion.enviar_mensaje()

        else:
            print("Lamentamos que no hayas encontrado un conductor para tu viaje. ¡Vuelve pronto!")

    def ver_viajes(self, data_list, correo_usuario):
        """
        Función para mostrarle los viajes al usuario
        """
        ventana_viajes = tkinter.Tk()
        ventana_viajes.title("Tus viajes")
        ventana_viajes.geometry("550x650+50+50")
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
            button_volver = Button(ventana_viajes, text="Volver", command= ventana_viajes.destroy, font=("Segoe UI", 10))
            button_volver.pack(pady = 10)
            #print(i)
            #print(" Origen:", item["Origen"],"\n", "Destino:", item["Destino"],"\n", "Conductor:", item["Conductor"],"\n", "Matricula:", matricula.decode('latin-1'),"\n")
            i+=1
        ventana_viajes.mainloop()
        #print("¡Esperamos que disfrutes de tus viajes!")