import random
import os
import string
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa


ciudades = ["madrid", "barcelona", "lisboa", "oporto", "valencia", "sevilla", "zaragoza", "malaga", "lisboa", "porto", "bilbao", "vigo", "granada", "alicante", "cordoba", "valladolid", "gijon", "oviedo", "salamanca", "santander", "graz"]
apellidos = ["Garcia","Fernandez","Gonzalez","Lopez","Martinez","Rodriguez","Sanchez","Perez","Gomez","Martin","Jimenez","Ruiz","Hernandez","Diaz","Moreno","Alvarez","Romero","Alonso","Navarro","Torres","Dominguez","Vazquez","Ramos","Cabrera","Soto","Reyes","Iglesias","Ortega","Morales","Castro","Silva","Cortes","Pascual","Guerrero","Vega","Flores","Vidal","Molina","Arias","Santos","Cruz","Pena","Mendoza", "Aguilar","Serrano","Ortiz","Gimenez","Fuentes"]
nombres = ["Antonio", "Maria", "Manuel", "Carmen", "Jose", "Ana", "Javier", "Isabel", "Francisco", "Laura", "Miguel", "Raquel", "David", "Elena", "Carlos", "Beatriz", "Juan", "Natalia", "Pedro", "Sandra", "Luis", "Lucia", "Fernando", "Rocio", "Angel", "Silvia", "Diego", "Pilar", "Jose Luis", "Cristina", "Ruben", "Marta", "Pablo", "Patricia", "Manuela", "Teresa", "Jose Manuel", "Rosa", "Andres", "Sara", "Joaquin", "Gemma", "Rafael", "Nuria", "Enrique", "Lorena", "Victor", "Ines"]

class GeneradorDatos:
    def __init__(self, id):
        self.id = id
        self.nombre = self.nombre_completo()
        self.contador = random.randint(1, 6)
        self.consumo = random.uniform(5, 8).__round__(2)
        self.ruta_origen = self.ruta_origen()
        self.ruta_destino = self.ruta_destino()
        self.public_key = None

    def public_key(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self._public_key = private_key.public_key()

        return private_key

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
    
