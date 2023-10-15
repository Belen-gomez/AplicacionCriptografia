from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives import padding

class Usuario:
    def __init__(self):
       pass

    def cifrar_direccion(self, key, iv, key_hmac):
        direccion = input("¿Donde te recojo? ")
        padder = padding.PKCS7(128).padder()

        # Asegúrate de que 'direccion' es una cadena de bytes
        direccion_bytes = direccion.encode()

        # Rellena los datos
        direccion_rellenada = padder.update(direccion_bytes) + padder.finalize()

        clave_usuario = input("Introduce la clave con la que quieres cifrar el mensaje: ")

        # Ciframos la dirección con la clave del usuario
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ct = encryptor.update(direccion_rellenada) + encryptor.finalize()

        # Crea una instancia de HMAC con SHA256 y la clave generada
        h = hmac.HMAC(key_hmac, hashes.SHA256())

        # Autentica el texto cifrado
        h.update(ct)

        # Obtiene el MAC (Mensaje de Autenticación de Código)
        mac = h.finalize()


        return ct, mac