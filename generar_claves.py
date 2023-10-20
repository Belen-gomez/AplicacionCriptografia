from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


for i in range(1, 23):
    path = "conductores/" + str(i) + "/key.pem"
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
