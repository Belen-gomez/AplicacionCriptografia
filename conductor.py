from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import padding
import random
import string
import time
from cryptography.hazmat.primitives import padding as pd
from cryptography.hazmat.primitives import serialization
from base_de_pasajeros import BaseDePasajeros

class Conductor:
    def __init__(self, nombre, id):
        self.nombre = nombre
        self.id = id
        self._public_key = None
        self.__private_key = self.key()
        self.__clave_simetrica = None
        self.__iv = None
        self.__key_hmac = None

    def key(self):
        path = "conductores/" + str(self.id) + "/key.pem"
        with open(path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
            )
        ''' private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )'''
        self._public_key = private_key.public_key()

        return private_key
    
    def cifrado_simetrico(self, clave_cifrada, iv_cifrado, clave_hmac):
        key = self.__private_key.decrypt(
            clave_cifrada,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        iv = self.__private_key.decrypt(
            iv_cifrado,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        key_hmac = self.__private_key.decrypt(
            clave_hmac,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        self.__clave_simetrica = key
        self.__iv = iv
        self.__key_hmac = key_hmac

        
    def descifrar_direccion(self, direccion_cifrada, mac_direccion, correo_usuario):
        cipher = Cipher(algorithms.AES(self.__clave_simetrica), modes.CBC(self.__iv))
        decryptor = cipher.decryptor()
        direccion_descifrada = decryptor.update(direccion_cifrada) + decryptor.finalize()

        # Quitamos el padding
        unpadder = pd.PKCS7(128).unpadder()
        direccion = unpadder.update(direccion_descifrada) + unpadder.finalize()
        h = hmac.HMAC(self.__key_hmac, hashes.SHA256())
        h.update(direccion)
        h.verify(mac_direccion)
        print("He recibido correctamente tu dirección")
        
        path = "conductores/" + str(self.id) + "/pasajeros.json"
        ciphertext = self._public_key.encrypt(direccion,
                padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))
        pasajero = {"Correo": correo_usuario, "Direccion": ciphertext.decode("latin-1")}
        pasajeros = BaseDePasajeros()
        pasajeros.FILE_PATH = path
        pasajeros.load_store()
        pasajeros.add_item(pasajero)
        pasajeros.save_store()
        time.sleep(1)
        print("Ya estás apuntado para el viaje")

    def cifrar_matricula(self):
        print("--------- SISTEMA ---------")
        print("Cifrando matricula")
        time.sleep(2)
        print("--------- FIN ---------")
        digitos = ''.join(random.choice(string.digits) for _ in range(4))
        letras = ''.join(random.choice('BCDFGHJKLMNPQRSTVWXYZ') for _ in range(3))
        matricula = digitos + letras
        h = hmac.HMAC(self.__key_hmac, hashes.SHA256())

        # Autentica el texto cifrado
        h.update(matricula.encode())

        # Obtiene el MAC (Mensaje de Autenticación de Código)
        mac = h.finalize()
        padder = pd.PKCS7(128).padder()
        matricula_bytes = matricula.encode()
        matricula_rellenada = padder.update(matricula_bytes) + padder.finalize()

        # Ciframos la matrícula con la clave simétrica
        cipher = Cipher(algorithms.AES(self.__clave_simetrica), modes.CBC(self.__iv))
        encryptor = cipher.encryptor()
        ct = encryptor.update(matricula_rellenada) + encryptor.finalize()


        return ct, mac