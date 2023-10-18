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
        time.sleep(5)
        print("¡Hola soy", self.conductor, "y te voy a llevar tu destino!")
        input("¿Qué tal estás?")
        print("Seguro que conmigo te lo pasas genial!!")
        time.sleep(2)
        print("Para reservar el viaje necesito saber donde recogerte. Cuando lo sepa te mandaré mi matrícula para que me reconozcas")
        clave_cifrada, iv = self.conductor.cifrado_simetrico(self.usuario._public_key)
        self.usuario.cifrado_simetrico(clave_cifrada, iv)

        direccion_cifrada = self.usuario.cifrar_direccion()

        #el conductor descifra el mensaje
        self.conductor.descifrar_direccion(direccion_cifrada)
        print("Ahora te voy a enviar mi matricula")
        matricula_cifrada = self.conductor.cifrar_matricula()
        self.usuario.descifrar_matricula(matricula_cifrada)
        
        print("¡Ya estamos listos para irnos!")
        
    """def cifrado_simetrico(self):
        key = os.urandom(32)
        key_hmac = os.urandom(32)
        iv = os.urandom(16)
        print("--------- SISTEMA ---------")
        print("Generando clave simétrica, esto puede tomar unos segundos...")
        time.sleep(5)
        print("La clave simétrica para esta comunicación es: ", key)
        print("--------- FIN ---------")

        direccion_cifrada, mac_direccion = Usuario().cifrar_direccion(key, iv, key_hmac)

        
        #el conductor descifra el mensaje
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        direccion_descifrada = decryptor.update(direccion_cifrada) + decryptor.finalize()

        # Quitamos el padding
        unpadder = padding.PKCS7(128).unpadder()
        direccion = unpadder.update(direccion_descifrada) + unpadder.finalize()

        # Crea una nueva instancia de HMAC con SHA256 y la misma clave
        h = hmac.HMAC(key_hmac, hashes.SHA256())

        # Autentica el texto cifrado nuevamente
        h.update(direccion_cifrada)

        # Verifica el MAC. Si el MAC no coincide, se lanzará una excepción.
        h.verify(mac_direccion)

        print("He recibido tu direccion correctamente")
        print("Ahora te voy a enviar mi matrícula cifrada con la clave simétrica")

        matricula_cifrada, mac_matricula= Conductor().cifrar_matricula(key, iv, key_hmac)
        print("Esta es mi matricula cifrada", matricula_cifrada)

        #el usuario descifra la matricula. Hay que ver lo de la clave
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        matricula_descifrado = decryptor.update(matricula_cifrada) + decryptor.finalize()

        # Quitamos el padding
        unpadder = padding.PKCS7(128).unpadder()
        matricula = unpadder.update(matricula_descifrado) + unpadder.finalize()

        h = hmac.HMAC(key_hmac, hashes.SHA256())

        # Autentica el texto cifrado nuevamente
        h.update(matricula_cifrada)

        # Verifica el MAC. Si el MAC no coincide, se lanzará una excepción.
        h.verify(mac_matricula)"""

        




