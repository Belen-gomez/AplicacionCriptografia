"""
1. iniciar sesion
    a. Si no tienes cuenta, registrarse. Guardar la contraseña en una base de datos con el correo y el salt

"""

import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def Registro():
    None
def InicioSesion():
    print(4)
# Salts should be randomly generated
salt = os.urandom(16)
# derive
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480000,
)
key = kdf.derive(b"my great password")
# verify
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480000,
)
print(kdf.verify(b"my great password", key))

while True:
    a = input("Tienes cuenta? (S/N)")
    if a == "S":
        InicioSesion()
        break
    elif a == "N":
        Registro()
        break
