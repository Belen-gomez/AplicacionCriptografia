import random
import os
import string
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ciudades = ["madrid", "barcelona", "lisboa", "oporto", "valencia", "sevilla", "zaragoza", "malaga", "lisboa", "porto", "bilbao", "vigo", "granada", "alicante", "cordoba", "valladolid", "gijon", "oviedo", "salamanca", "santander", "graz"]
apellidos = ["Garcia","Fernandez","Gonzalez","Lopez","Martinez","Rodriguez","Sanchez","Perez","Gomez","Martin","Jimenez","Ruiz","Hernandez","Diaz","Moreno","Alvarez","Romero","Alonso","Navarro","Torres","Dominguez","Vazquez","Ramos","Cabrera","Soto","Reyes","Iglesias","Ortega","Morales","Castro","Silva","Cortes","Pascual","Guerrero","Vega","Flores","Vidal","Molina","Arias","Santos","Cruz","Pena","Mendoza", "Aguilar","Serrano","Ortiz","Gimenez","Fuentes"]
nombres = ["Antonio", "Maria", "Manuel", "Carmen", "Jose", "Ana", "Javier", "Isabel", "Francisco", "Laura", "Miguel", "Raquel", "David", "Elena", "Carlos", "Beatriz", "Juan", "Natalia", "Pedro", "Sandra", "Luis", "Lucia", "Fernando", "Rocio", "Angel", "Silvia", "Diego", "Pilar", "Jose Luis", "Cristina", "Ruben", "Marta", "Pablo", "Patricia", "Manuela", "Teresa", "Jose Manuel", "Rosa", "Andres", "Sara", "Joaquin", "Gemma", "Rafael", "Nuria", "Enrique", "Lorena", "Victor", "Ines"]

class Conductor:
    def __init__(self, id):
        self.id = id
        self.nombre = self.nombre_completo()
        self.contador = random.randint(1, 6)
        ''' self.matricula = self.matricula_encode()[0]
        self.salt = self.matricula_encode()[1] '''
        self.consumo = random.uniform(5, 8).__round__(2)
        self.ruta_origen = self.ruta_origen()
        self.ruta_destino = self.ruta_destino()

    ''' def matricula_encode(self):
        digitos = ''.join(random.choice(string.digits) for _ in range(4))
        letras = ''.join(random.choice('BCDFGHJKLMNPQRSTVWXYZ') for _ in range(3))
        matricula = digitos + letras
        salt = os.urandom(16)
        # derive
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        matricula_derivada = kdf.derive(matricula.encode("utf-8"))

        return base64.b64encode(matricula_derivada).decode('utf-8'),  base64.b64encode(salt).decode('utf-8') '''


    def ruta_origen(self):
        num = random.randint(0, len(ciudades)-1)
        return ciudades[num]

    def ruta_destino(self):
        num = random.randint(0, len(ciudades)-1)
        destino = ciudades[num]
        while destino == self.ruta_origen:
            num = random.randint(0, len(ciudades)-1)
            destino = ciudades[num]
        return destino
    
    def nombre_completo(self):
        num = random.randint(0, len(nombres)-1)
        nombre = nombres[num]
        num = random.randint(0, len(apellidos)-1)
        apellido = apellidos[num]
        return nombre +" "+ apellido