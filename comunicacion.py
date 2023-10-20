from base_conductores import BaseDeConductores
import os
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives import padding
import random
import string
from usuario import Usuario
from conductor import Conductor

class Comunicacion:
    
    def __init__(self, nombre_conductor, id, correo, nombre_usuario):
         self.usuario = self.crear_usuario(correo, nombre_usuario)
         self.conductor = self.crear_conductor(nombre_conductor, id)

    def crear_usuario(self, correo, nombre_usuario):
        usuario = Usuario(correo, nombre_usuario)
        return usuario
    
    def crear_conductor(self, nombre_conductor, id):
        conductor=Conductor(nombre_conductor, id)
        return conductor
    
    def enviar_mensaje(self):
        os.system("cls")
        time.sleep(2)
        print("¡Hola soy", self.conductor.nombre, "y te voy a llevar tu destino!")
        input("¿Qué tal estás?")
        print("Seguro que conmigo te lo pasas genial!!")
        time.sleep(1)
        print("Para reservar el viaje necesito saber donde recogerte. Cuando lo sepa te mandaré mi matrícula para que me reconozcas")
        clave_cifrada, iv, clave_hmc = self.usuario.cifrado_simetrico(self.conductor._public_key)
        self.conductor.cifrado_simetrico(clave_cifrada, iv, clave_hmc)

        
        direccion_cifrada, mac_direccion = self.usuario.cifrar_direccion()

        #el conductor descifra el mensaje
        self.conductor.descifrar_direccion(direccion_cifrada, mac_direccion, self.usuario.correo)
        time.sleep(2)
        print("Ahora te voy a enviar mi matricula")

        matricula_cifrada, mac_matricula = self.conductor.cifrar_matricula()
        self.usuario.descifrar_matricula(matricula_cifrada, mac_matricula)
        
        conductores = BaseDeConductores()

        conductor_sel = conductores.find_data_id(self.conductor.id)

        conductor_sel["contador"] -= 1

        conductores.save_store()
        print("¡Ya estamos listos para irnos!")
        
    