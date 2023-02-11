import json

from unittest import TestCase

#from faker import faker
#from faker.generator import random

from app import app

class testOffers(TestCase):

    def SetUp(self):
        self.token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3NTY3OTIwMSwianRpIjoiYzVmZTMyMDYtYTRlOS00NTM1LTgzZjItYWE2ODYzYWYwYzUwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNjc1Njc5MjAxLCJleHAiOjE2NzU2ODEwMDF9.x4_TRRiMgFb1Y9DgHIO97ndsfS1kvdJfiMombM9cWpM"
        self.userId=1

    def prueba_ping(self):
        endpoint_ping='/offers/ping'
        solicitud_ping=self.client.get(endpoint_ping)
        respuesta_ping=json.loads(solicitud_ping.get_data())
        mensaje=respuesta_ping["Mensaje"]
        self.assertEqual(mensaje, "Pong")

    #def crear_oferta(self):
    #    headers={
    #        'Content-Type': 'application/json',
    #        'Authorization': 'Bearer {}'.format(self.token)
    #    }

    #    endpoint_ofertas='/offers'