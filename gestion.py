from base_conductores import BaseDeConductores
from base_de_pasajeros import BaseDePasajeros
from comunicacion import Comunicacion
import time
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
    
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

    def reservar(self, correo_usuario, nombre):
        """
        Función para rerservar un viaje
        """
        conductores = BaseDeConductores()
        conductores.load_store()
        print("Viajes disponibles")
        for item in conductores._data_list:
            if item["contador"] != 0:
                print("Origen: ", item["ruta_origen"], " - Destino: ", item["ruta_destino"])
            
        #Se pide el viaje
        origen = input("¿Dónde quieres empezar tu viaje? ").lower()
        destino = input("¿A dónde quieres ir? ").lower()
       
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
        #Se descifra la matrícula
        path = os.path.dirname(__file__) + "/usuarios/" + correo_usuario + "/key.pem"
        with open(path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
            )
        print("Estos son tus viajes reservados:")    #Se muestran todos los viajes
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
            print(i)
            print(" Origen:", item["Origen"],"\n", "Destino:", item["Destino"],"\n", "Conductor:", item["Conductor"],"\n", "Matricula:", matricula.decode('latin-1'),"\n")
            i+=1
        print("¡Esperamos que disfrutes de tus viajes!")