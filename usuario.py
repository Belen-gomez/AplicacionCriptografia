from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa

class Usuario:
    def __init__(self, correo, nombre):
       self.nombre = nombre
       self.correo = correo
       self._public_key = None
       self.__private_key = self.key()
       self.__clave_simetrica = None
       self.iv = None
       self.key_hmac = None

    def key(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self._public_key = private_key.public_key()

        return private_key
    
    def cifrado_simetrico(self, clave_cifrada, iv, key_hmac):
        key = self.__private_key.decrypt(
                clave_cifrada,
                padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        self.__clave_simetrica = key
        self.iv = iv
        self.key_hmac = key_hmac
        
    def cifrar_direccion(self):
        direccion = input("¿Donde te recojo? ")
        from cryptography.hazmat.primitives import padding
        padder = padding.PKCS7(128).padder()

        # Asegúrate de que 'direccion' es una cadena de bytes
        direccion_bytes = direccion.encode()

        # Rellena los datos
        direccion_rellenada = padder.update(direccion_bytes) + padder.finalize()

        # Ciframos la dirección con la clave del usuario
        cipher = Cipher(algorithms.AES(self.__clave_simetrica), modes.CBC(self.iv))
        encryptor = cipher.encryptor()
        ct = encryptor.update(direccion_rellenada) + encryptor.finalize()

        # Crea una instancia de HMAC con SHA256 y la clave generada
        h = hmac.HMAC(self.key_hmac, hashes.SHA256())

        # Autentica el texto cifrado
        h.update(ct)

        # Obtiene el MAC (Mensaje de Autenticación de Código)
        mac = h.finalize()


        return ct, mac
    
    def descifrar_matricula(self, matricula_cifrada, mac_matricula):
        h = hmac.HMAC(self.key_hmac, hashes.SHA256())
        h.update(matricula_cifrada)
        h.verify(mac_matricula)

        cipher = Cipher(algorithms.AES(self.__clave_simetrica), modes.CBC(self.iv))
        decryptor = cipher.decryptor()
        matricula_descifrado = decryptor.update(matricula_cifrada) + decryptor.finalize()

        # Quitamos el padding
        from cryptography.hazmat.primitives import padding
        unpadder = padding.PKCS7(128).unpadder()
        matricula = unpadder.update(matricula_descifrado) + unpadder.finalize()
        print("matricula", matricula)