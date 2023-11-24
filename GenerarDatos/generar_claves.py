from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import os
from claves_conductores import ClavesConductores
from base_conductores import BaseDeConductores 
import json
import random
import string
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509
from cryptography.x509.oid import NameOID
import datetime

def CrearMatricula():
    """Crea las matrículas de los conductores y las guarda encriptadas en un json"""
    for i in range(1, 24):
        digitos = ''.join(random.choice(string.digits) for _ in range(4))
        letras = ''.join(random.choice('BCDFGHJKLMNPQRSTVWXYZ') for _ in range(3))
        matricula = digitos + letras
        path = "/DATOS/BELÉN/3º UNI/Criptografía/Practica_1/Criptografia/conductores/" + str(i) + "/matricula.json"
        path_abrir = "/DATOS/BELÉN/3º UNI/Criptografía/Practica_1/Criptografia/conductores/" + str(i) + "/key.pem"
        with open(path_abrir, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None, 
            )
        public_key = private_key.public_key()
        ciphertext = public_key.encrypt(matricula.encode('latin-1'),
                    padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                ))
        data = [{"Matricula": ciphertext.decode('latin-1')}]
        with open(path, 'w') as outfile:
            json.dump(data, outfile)
    
def GuardarClavesPublicas():
    """A partir de la clave privada de cada conductor, se genera la pública y se guarda en un json público"""
    for i in range(1, 24):
        path = "/DATOS/BELÉN/3º UNI/Criptografía/Practica_1/Criptografia/conductores/" + str(i) + "/key.pem"
        with open(path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
            )
        public_key = private_key.public_key()
        bd = ClavesConductores()
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        pem = pem.decode('latin-1')
        pem = pem.replace("-----BEGIN PUBLIC KEY-----\n", "")
        pem = pem.replace("\n-----END PUBLIC KEY-----\n", "")
        # Guardar la clave pública en un archivo JSON
        bd.add_item({"Id": i, "Clave_publica": pem})
        
def GenerarClavePrivada():
    """Genera las claves privadas de los conductores y las guarda en un archivo .pem"""
    for i in range(1, 24):
        path = "conductores/" + str(i) + "/key.pem"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        private_key = rsa.generate_private_key(
                            public_exponent=65537,
                            key_size=2048,
                        )

        with open(path, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
