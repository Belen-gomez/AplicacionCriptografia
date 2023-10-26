from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from claves_usuarios import ClavesUsuarios

class Claves():
    def __init__(self, path, id):
        self.path = path
        self.id = id
    
    def CrearClavePrivada(self):
        """
        Crea la clave privada del los usuarios cuando se registran. Depués se guarda la clave pública en una base datos pública.
        """
        private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                )

        with open(self.path, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        public_key = private_key.public_key()
        bd = ClavesUsuarios()
        pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
        pem = pem.decode('latin-1')
        pem = pem.replace("-----BEGIN PUBLIC KEY-----\n", "")
        pem = pem.replace("\n-----END PUBLIC KEY-----\n", "")
        bd.add_item({"Correo": self.id, "Clave_publica": pem})

