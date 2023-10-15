from base_conductores import BaseDeConductores


class Comunicacion():
    
    def __innit__(self, conductor: str, usuario: str):
        self.conductor = conductor
        self.usuario = usuario

    def enviar_mensaje(self):
        print("¡Hola soy", self.conductor, "y te voy a llevar tu destino!")
        input("¿Qué tal estás?")
        print("Seguro que conmigo te lo pasas genial!!")
        print("Para reservar el viaje necesito saber donde recogerte. Cuando lo sepa te mandaré mi matrícula para que me reconozcas")
        
       