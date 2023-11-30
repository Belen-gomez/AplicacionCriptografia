from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os
from cryptography.hazmat.primitives import padding as pd
from cryptography.hazmat.primitives import serialization
import json
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
import datetime
from AC.ac_raiz.ac_raiz import AC_raiz
from AC.ac_conductor.ac_conductores import AC_conductor
from base_conductores import BaseDeConductores

ahora = datetime.datetime.now()

class Conductor:
    def __init__(self, nombre, id):
        self.nombre = nombre
        self.id = id
        self._public_key = None
        self.__private_key = self.key()
        self.__clave_simetrica = None
        self.__iv = None

    def GenerarSolicitudCertificado(self):
        conductores = BaseDeConductores()
        conductores.load_store()
        item = conductores.find_data_id(self.id)
        origen = item["ruta_origen"]

        csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        # Provide various details about who we are.
        x509.NameAttribute(NameOID.USER_ID, str(self.id)),
        x509.NameAttribute(NameOID.COMMON_NAME, self.nombre),
        x509.NameAttribute(NameOID.LOCALITY_NAME, origen),
         x509.NameAttribute(NameOID.COMMON_NAME, "hailo.com"),
        ])).add_extension(
            x509.SubjectAlternativeName([
            # Describe what sites we want this certificate for.
            x509.DNSName("hailo.com"),
            x509.DNSName("www.hailo.com"),
            x509.DNSName("subdomain.hailo.com"),
        ]),
        critical=False,).sign(self.__private_key, hashes.SHA256())

        raiz = AC_conductor()
        certificado = raiz.verificar_firma_csr(csr, self._public_key)

        with open(os.path.dirname(__file__) +"/"+ str(self.id) + "/certificado.pem", "wb") as f:
            f.write(certificado.public_bytes(serialization.Encoding.PEM))

        return certificado
    
    def key(self):
        #Se recupera su clave privada
        path = os.path.dirname(__file__) +"/"+ str(self.id) + "/key.pem"
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

        ac_conductor = AC_conductor()
        certificado_ac_conductor = ac_conductor.certificado

        with open(os.path.dirname(__file__) + "/"+ str(self.id) + "/certificado.pem", "rb") as f:
            certificado_conductor_pem = f.read()
        certificado_conductor = x509.load_pem_x509_certificate(certificado_conductor_pem, default_backend())
        if certificado_conductor.not_valid_after < ahora:
            certificado_conductor = self.GenerarSolicitudCertificado()
    
        return certificado_raiz, certificado_ac_conductor, certificado_conductor
    
    def VerificarCertificados(self, ac_raiz, ac_usuario, usuario):
            #Se verifica la cadena de certificados
        try:
            ac_usuario.public_key().verify(
                usuario.signature,
                usuario.tbs_certificate_bytes,
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            
            ac_raiz.public_key().verify(
                ac_usuario.signature, 
                ac_usuario.tbs_certificate_bytes,
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except Exception as e:
            print(f"Error al verificar la cadena de certificados: {e}")
            print("Detalles de la AC raiz:")
            print(ac_raiz)
            print("Detalles de la AC usuario:")
            print(ac_usuario)
            print("Detalles del certificado del usuario:")
            print(usuario)
            return False
    
    def cifrado_simetrico(self, clave_cifrada, iv_cifrado):
        #El conductor desencriota las claves de la comunicación con su clave privada

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
        self.__clave_simetrica = key
        self.__iv = iv
        
    def descifrar_direccion(self, direccion_cifrada, sign_direccion, correo_usuario, usuario_public_key, ac_raiz, ac_usuario, usuario):
        #Desecripta la dirección
        cipher = Cipher(algorithms.AES(self.__clave_simetrica), modes.CBC(self.__iv))
        decryptor1 = cipher.decryptor()
        direccion_descifrada = decryptor1.update(direccion_cifrada) + decryptor1.finalize()
        unpadder = pd.PKCS7(128).unpadder()
        direccion = unpadder.update(direccion_descifrada) + unpadder.finalize()
       
        #se comprueba la integridad del mensaje y la firma
        usuario_public_key.verify(
                    sign_direccion,
                    direccion,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
        )
        self.VerificarCertificados(ac_raiz, ac_usuario, usuario)
        
        #se alamcena la direccion del usuario
        ciphertext = self._public_key.encrypt(direccion,
                padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))
        pasajero = {"Correo": correo_usuario, "Direccion": ciphertext.decode("latin-1")}
        
        return pasajero

    def cifrar_matricula(self):
        data_list = []
        #se recupera la matricula
        path = os.path.dirname(__file__) +"/"+ str(self.id) + "/matricula.json"
        with open(path, "r") as file:
            data_list = json.load(file)
        
        #se desencripta con la clave privada del conductor
        matricula_cifrada= data_list[0]["Matricula"]
        matricula = self.__private_key.decrypt(
            matricula_cifrada.encode('latin-1'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        padder = pd.PKCS7(128).padder()
        matricula_rellenada = padder.update(matricula) + padder.finalize()

        # Ciframos la matrícula con la clave simétrica
        cipher = Cipher(algorithms.AES(self.__clave_simetrica), modes.CBC(self.__iv))
        encryptor = cipher.encryptor()
        ct = encryptor.update(matricula_rellenada) + encryptor.finalize()

        #Se firma la matricula
        sign_mac = self.__private_key.sign(
                    matricula,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
        )
        ac_raiz, ac_conductor, conductor = self.ObtenerCertificados()
        return ct, sign_mac, ac_raiz, ac_conductor, conductor
