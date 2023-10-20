from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

class Claves():
    def __init__(self, path):
        self.path = path
    
    def CrearClavePrivada(self):
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

