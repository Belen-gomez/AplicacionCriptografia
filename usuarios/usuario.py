from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
import os
import time
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import padding as pd

class Usuario:
    def __init__(self, correo, nombre):
       self.nombre = nombre
       self.correo = correo
       self._public_key = None
       self.__private_key = self.key()
       self.__clave_simetrica = None
       self.__iv = None
       self.__key_hmac = None

    def key(self):
        #Se recupera su clave privada
        path = os.path.dirname(__file__) + "/"+ self.correo +  "/key.pem"
        with open(path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
            )
        self._public_key = private_key.public_key()

        return private_key
    
    def cifrado_simetrico(self, public_key_conductor):
        #El usuario genera las claves de la comunicación y las encripta con la clave pública del conductor
        key = os.urandom(32)
        key_hmac = os.urandom(32)
        iv = os.urandom(16)

        ciphertext = public_key_conductor.encrypt(key,
                padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))
        ciphertext_iv = public_key_conductor.encrypt(iv,
              padding.OAEP(
                  mgf=padding.MGF1(algorithm=hashes.SHA256()),
                  algorithm=hashes.SHA256(),
                  label=None
              ))
        ciphertext_hmac = public_key_conductor.encrypt(key_hmac,
                  padding.OAEP(
                      mgf=padding.MGF1(algorithm=hashes.SHA256()),
                      algorithm=hashes.SHA256(),
                      label=None
                  ))
        self.__clave_simetrica = key
        self.__iv = iv
        self.__key_hmac = key_hmac
        return ciphertext, ciphertext_iv, ciphertext_hmac
        
    def cifrar_direccion(self):
        direccion = input("¿Donde te recojo? ")
        print("--------- SISTEMA ---------")
        print("Cifrando direccion")
        time.sleep(2)
        print("--------- FIN ---------")

        # Crea una instancia de HMAC con SHA256 y la clave generada
        h = hmac.HMAC(self.__key_hmac, hashes.SHA256())
        # Autentica el texto cifrado
        direccion_bytes = direccion.encode()

        h.update(direccion_bytes)

        # Obtiene el MAC (Mensaje de Autenticación de Código)
        mac = h.finalize()
    
        padder = pd.PKCS7(128).padder()
        # Rellena los datos
        direccion_rellenada = padder.update(direccion_bytes) + padder.finalize()

        # Ciframos la dirección con la clave del usuario
        cipher = Cipher(algorithms.AES(self.__clave_simetrica), modes.CBC(self.__iv))
        encryptor1 = cipher.encryptor()
        ct = encryptor1.update(direccion_rellenada) + encryptor1.finalize()

        # Crear un nuevo encryptor para 'mac'
        encryptor2 = cipher.encryptor()
        #Se encripta el mac
        ct_mac = encryptor2.update(mac) + encryptor2.finalize()
        return ct, ct_mac
    
    def descifrar_matricula(self, matricula_cifrada, mac_matricula):
        #Se descifra la matrícula y ek mac
        cipher = Cipher(algorithms.AES(self.__clave_simetrica), modes.CBC(self.__iv))
        decryptor = cipher.decryptor()
        decryptor2 = cipher.decryptor()
        matricula_descifrado = decryptor.update(matricula_cifrada) + decryptor.finalize()
        mac = decryptor2.update(mac_matricula) + decryptor2.finalize()

        # Quitamos el padding
        unpadder = pd.PKCS7(128).unpadder()
        matricula = unpadder.update(matricula_descifrado) + unpadder.finalize()
        #Se comprueba que la dirección no ha sido manipulada
        h = hmac.HMAC(self.__key_hmac, hashes.SHA256())
        h.update(matricula)
        h.verify(mac)

        ciphertext = self._public_key.encrypt(matricula,
                padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))
        return ciphertext