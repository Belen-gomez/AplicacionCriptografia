from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
import os
import time
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import padding as pd
from cryptography import x509
from cryptography.hazmat.backends import default_backend


class Usuario:
    def __init__(self, correo, nombre):
       self.nombre = nombre
       self.correo = correo
       self._public_key = None
       self.__private_key = self.key()
       self.__clave_simetrica = None
       self.__iv = None
       #self.__key_hmac = None

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
    
    def ObtenerCertificados(self):
        with open(os.path.dirname(__file__) + "/../AC/ac_raiz/certificado.pem", "rb") as f:
            certificado_raiz_pem = f.read()
        certificado_raiz = x509.load_pem_x509_certificate(certificado_raiz_pem, default_backend())

        with open(os.path.dirname(__file__) + "/../AC/ac_usuario/certificado.pem", "rb") as f:
            certificado_ac_conductor_pem = f.read()
        certificado_ac_conductor = x509.load_pem_x509_certificate(certificado_ac_conductor_pem, default_backend())

        with open(os.path.dirname(__file__) + "/"+ self.correo + "/certificado.pem", "rb") as f:
            certificado_conductor_pem = f.read()
        certificado_conductor = x509.load_pem_x509_certificate(certificado_conductor_pem, default_backend())
    
        return certificado_raiz, certificado_ac_conductor, certificado_conductor
    
    def VerificarCertificados(self, ac_raiz, ac_conductor, conductor):
        #Se verifica la cadena de certificados
        try:
            ac_raiz.public_key().verify(
                ac_conductor.signature,
                ac_conductor.tbs_certificate_bytes,
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            ac_conductor.public_key().verify(
                conductor.signature,
                conductor.tbs_certificate_bytes,
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except Exception as e:
            print(f"Error al verificar la cadena de certificados: {e}")
            print("Detalles de la AC raiz:")
            print(ac_raiz)
            print("Detalles de la AC conductor:")
            print(ac_conductor)
            print("Detalles del certificado del conductor:")
            print(conductor)
            return False
    
    def cifrado_simetrico(self, public_key_conductor):
        #El usuario genera las claves de la comunicación y las encripta con la clave pública del conductor
        key = os.urandom(32)
        ''' key_hmac = os.urandom(32) '''
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
        ''' ciphertext_hmac = public_key_conductor.encrypt(key_hmac,
                  padding.OAEP(
                      mgf=padding.MGF1(algorithm=hashes.SHA256()),
                      algorithm=hashes.SHA256(),
                      label=None
                  )) '''
        self.__clave_simetrica = key
        self.__iv = iv
        '''  self.__key_hmac = key_hmac '''
        return ciphertext, ciphertext_iv 
        
    def cifrar_direccion(self):
        direccion = input("¿Donde te recojo? ")
        print("--------- SISTEMA ---------")
        print("Cifrando direccion")
        time.sleep(2)
        print("--------- FIN ---------")

        # Crea una instancia de HMAC con SHA256 y la clave generada
        h = hmac.HMAC(self.__clave_simetrica, hashes.SHA256())
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
        #encryptor2 = cipher.encryptor()
        #Se encripta el mac
        #ct_mac = encryptor2.update(mac) + encryptor2.finalize()
        sing_mac = self.__private_key.sign(
                    mac,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()

        )
        ac_raiz, ac_usuario , usuario = self.ObtenerCertificados()

        return ct, sing_mac, ac_raiz, ac_usuario , usuario
    
    def descifrar_matricula(self, matricula_cifrada, sign_matricula, public_key_conductor, ac_raiz, ac_conductor, conductor):
        #Se descifra la matrícula y el mac
        cipher = Cipher(algorithms.AES(self.__clave_simetrica), modes.CBC(self.__iv))
        decryptor = cipher.decryptor()
        #decryptor2 = cipher.decryptor()
        matricula_descifrado = decryptor.update(matricula_cifrada) + decryptor.finalize()
        #mac = decryptor2.update(mac_matricula) + decryptor2.finalize()

        # Quitamos el padding
        unpadder = pd.PKCS7(128).unpadder()
        matricula = unpadder.update(matricula_descifrado) + unpadder.finalize()
        #Se comprueba que la dirección no ha sido manipulada
        h = hmac.HMAC(self.__clave_simetrica, hashes.SHA256())
        h.update(matricula)
        mac = h.finalize()

        public_key_conductor.verify(
                    sign_matricula,
                    mac,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
        )
        self.VerificarCertificados(ac_raiz, ac_conductor, conductor)
        print("Esta es mi matrícula: ", matricula.decode("latin-1"))
        ciphertext = self._public_key.encrypt(matricula,
                padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))
        return ciphertext