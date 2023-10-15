from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives import padding
import random
import string

class Matricula:
    def __init__(self):
        pass

    def cifrar_matricula(self, key, iv, key_hmac):
        digitos = ''.join(random.choice(string.digits) for _ in range(4))
        letras = ''.join(random.choice('BCDFGHJKLMNPQRSTVWXYZ') for _ in range(3))
        matricula = digitos + letras
        padder = padding.PKCS7(128).padder()
        matricula_bytes = matricula.encode()
        matricula_rellenada = padder.update(matricula_bytes) + padder.finalize()

        # Ciframos la matrícula con la clave simétrica
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ct = encryptor.update(matricula_rellenada) + encryptor.finalize()

        h = hmac.HMAC(key_hmac, hashes.SHA256())

        # Autentica el texto cifrado
        h.update(ct)

        # Obtiene el MAC (Mensaje de Autenticación de Código)
        mac = h.finalize()

        return ct, mac