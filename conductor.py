from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import padding
import random
import string
from cryptography.hazmat.primitives.asymmetric import rsa
import time
import os
from cryptography.hazmat.primitives import padding as pd

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
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
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

        
    def descifrar_direccion(self, direccion_cifrada, mac_direccion):
        cipher = Cipher(algorithms.AES(self.__clave_simetrica), modes.CBC(self.__iv))
        decryptor = cipher.decryptor()
        direccion_descifrada = decryptor.update(direccion_cifrada) + decryptor.finalize()

        # Quitamos el padding
        unpadder = pd.PKCS7(128).unpadder()
        direccion = unpadder.update(direccion_descifrada) + unpadder.finalize()
        h = hmac.HMAC(self.__key_hmac, hashes.SHA256())
        h.update(direccion)
        h.verify(mac_direccion)
        print(direccion)
        print("He recibido correctamente tu dirección")


    def cifrar_matricula(self):
        digitos = ''.join(random.choice(string.digits) for _ in range(4))
        letras = ''.join(random.choice('BCDFGHJKLMNPQRSTVWXYZ') for _ in range(3))
        matricula = digitos + letras
        h = hmac.HMAC(self.__key_hmac, hashes.SHA256())

        # Autentica el texto cifrado
        h.update(matricula.encode())

        # Obtiene el MAC (Mensaje de Autenticación de Código)
        mac = h.finalize()
        from cryptography.hazmat.primitives import padding
        padder = padding.PKCS7(128).padder()
        matricula_bytes = matricula.encode()
        matricula_rellenada = padder.update(matricula_bytes) + padder.finalize()

        # Ciframos la matrícula con la clave simétrica
        cipher = Cipher(algorithms.AES(self.__clave_simetrica), modes.CBC(self.__iv))
        encryptor = cipher.encryptor()
        ct = encryptor.update(matricula_rellenada) + encryptor.finalize()


        return ct, mac