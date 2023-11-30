from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
import os
import time
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import padding as pd
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
import datetime
from AC.ac_raiz.ac_raiz import AC_raiz
from AC.ac_usuario.ac_usuarios import AC_usuario
ahora = datetime.datetime.now()

class Usuario:
    def __init__(self, correo, nombre):
       self.nombre = nombre
       self.correo = correo
       self._public_key = None
       self.__private_key = self.key()
       self.__clave_simetrica = None
       self.__iv = None
    
    def GenerarSolicitudCertificado(self):
        csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
            # Provide various details about who we are.
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, self.id),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(NameOID.SURNAME, self.nombre),
            x509.NameAttribute(NameOID.COMMON_NAME, "hailo.com"),
        ])).add_extension(
            x509.SubjectAlternativeName([
                # Describe what sites we want this certificate for.
                x509.DNSName("hailo.com"),
                x509.DNSName("www.hailo.com"),
                x509.DNSName("subdomain.hailo.com"),
            ]),
            critical=False, ).sign(self.private_key, hashes.SHA256())
        usuario = AC_usuario()
        certificado = usuario.verificar_firma_csr(csr, self._public_key)

        with open(os.path.dirname(__file__) + "/"+ self.correo + "/certificado.pem", "wb") as f:
            f.write(certificado.public_bytes(serialization.Encoding.PEM))

        return certificado
    
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
        raiz = AC_raiz()
        certificado_raiz = raiz.certificado

        ac_usuario = AC_usuario()
        certificado_ac_usuario = ac_usuario.certificado
        
        with open(os.path.dirname(__file__) + "/"+ self.correo + "/certificado.pem", "rb") as f:
            certificado_usuario_pem = f.read()
        certificado_usuario = x509.load_pem_x509_certificate(certificado_usuario_pem, default_backend())
        if certificado_usuario.not_valid_after < ahora:
            certificado_usuario = self.GenerarSolicitudCertificado()
    
        return certificado_raiz, certificado_ac_usuario, certificado_usuario
    
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
    
        self.__clave_simetrica = key
        self.__iv = iv
        return ciphertext, ciphertext_iv 
        
    def cifrar_direccion(self, direccion: str):
        direccion_bytes = direccion.encode()    
        padder = pd.PKCS7(128).padder()
        # Rellena los datos
        direccion_rellenada = padder.update(direccion_bytes) + padder.finalize()

        # Ciframos la dirección con la clave del usuario
        cipher = Cipher(algorithms.AES(self.__clave_simetrica), modes.CBC(self.__iv))
        encryptor1 = cipher.encryptor()
        ct = encryptor1.update(direccion_rellenada) + encryptor1.finalize()

        # Se firma la dirección con la clave privada del usuario
        sing_mac = self.__private_key.sign(
                    direccion.encode(),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()

        )
        ac_raiz, ac_usuario , usuario = self.ObtenerCertificados()

        return ct, sing_mac, ac_raiz, ac_usuario , usuario
    
    def descifrar_matricula(self, matricula_cifrada, sign_matricula, public_key_conductor, ac_raiz, ac_conductor, conductor):
        #Se descifra la matrícula
        cipher = Cipher(algorithms.AES(self.__clave_simetrica), modes.CBC(self.__iv))
        decryptor = cipher.decryptor()
        matricula_descifrado = decryptor.update(matricula_cifrada) + decryptor.finalize()

        # Quitamos el padding
        unpadder = pd.PKCS7(128).unpadder()
        matricula = unpadder.update(matricula_descifrado) + unpadder.finalize()

        #Se verifica la integridad del mensaje y la firma
        public_key_conductor.verify(
                    sign_matricula,
                    matricula,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
        )
        self.VerificarCertificados(ac_raiz, ac_conductor, conductor)
        ciphertext = self._public_key.encrypt(matricula,
                padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))
        return ciphertext, matricula.decode("latin-1")