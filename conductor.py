from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import padding
import random
import string
from cryptography.hazmat.primitives.asymmetric import rsa
import time
import os

class Conductor:
    def __init__(self, nombre, id):
        self.nombre = nombre
        self.id = id
        self._public_key = None
        self.__private_key = self.key()
        self.__clave_simetrica = None
        self.iv = None

    def key(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self._public_key = private_key.public_key()

        return private_key
    
    def cifrado_simetrico(self, public_key_usuario):
        key = os.urandom(32)
        key_hmac = os.urandom(32)
        iv = os.urandom(16)
        print("--------- SISTEMA ---------")
        print("Generando clave simétrica, esto puede tomar unos segundos...")
        time.sleep(5)
        print("--------- FIN ---------")

        ciphertext = public_key_usuario.encrypt(key,
            padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))
        self.__clave_simetrica = key
        self.iv = iv
        return ciphertext, iv
        
    def descifrar_direccion(self, direccion_cifrada):
        cipher = Cipher(algorithms.AES(self.__clave_simetrica), modes.CBC(self.iv))
        decryptor = cipher.decryptor()
        direccion_descifrada = decryptor.update(direccion_cifrada) + decryptor.finalize()

        # Quitamos el padding
        from cryptography.hazmat.primitives import padding
        unpadder = padding.PKCS7(128).unpadder()
        direccion = unpadder.update(direccion_descifrada) + unpadder.finalize()
        print(direccion)
        print("He recibido correctamente tu dirección")

    def cifrar_matricula(self):
        digitos = ''.join(random.choice(string.digits) for _ in range(4))
        letras = ''.join(random.choice('BCDFGHJKLMNPQRSTVWXYZ') for _ in range(3))
        matricula = digitos + letras
        from cryptography.hazmat.primitives import padding
        padder = padding.PKCS7(128).padder()
        matricula_bytes = matricula.encode()
        matricula_rellenada = padder.update(matricula_bytes) + padder.finalize()

        # Ciframos la matrícula con la clave simétrica
        cipher = Cipher(algorithms.AES(self.__clave_simetrica), modes.CBC(self.iv))
        encryptor = cipher.encryptor()
        ct = encryptor.update(matricula_rellenada) + encryptor.finalize()

        #h = hmac.HMAC(key_hmac, hashes.SHA256())

        # Autentica el texto cifrado
        #h.update(ct)

        # Obtiene el MAC (Mensaje de Autenticación de Código)
        #mac = h.finalize()

        return ct#, mac