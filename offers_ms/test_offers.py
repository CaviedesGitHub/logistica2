import json
import time
from flask import Response
from flask_jwt_extended import create_access_token
from datetime import timedelta

from unittest import TestCase
from unittest.mock import Mock, patch

from app import app

class testOffers(TestCase):

    def setUp(self):
        self.client=app.test_client()
        self.userId=1
        self.offerId=1
        self.postId=1
        access_token_expires = timedelta(minutes=120)
        self.token=create_access_token(identity=self.userId, expires_delta=access_token_expires)
        access_token_expires = timedelta(seconds=3)
        self.tokenexpired=create_access_token(identity=self.userId, expires_delta=access_token_expires)
        #self.token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3NTczMTY3MywianRpIjoiOGU1OWJjZmQtNTJlYi00YzQ1LWI1NDUtZTU3MGYxMDBiNTQ0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MiwibmJmIjoxNjc1NzMxNjczLCJleHAiOjE2NzU3Mzg4NzN9.iPaNwx0Sp2TcPOyv5p12e7RyPAUDih3lrLxV0mVN43Q"
        #self.tokenexpired="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3NTY4NDg3NiwianRpIjoiZjdkYzNlN2QtMzFhNy00NWZhLTg3NjItNzIwZDQ0NTUyMWZjIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MiwibmJmIjoxNjc1Njg0ODc2LCJleHAiOjE2NzU2ODY2NzZ9.fPQFhAK_4k16NqpMGcT2eV-q-PQRUKHrLMiQY-xzDYM"

    def test_ping(self):
        endpoint_ping='/offers/ping'
        solicitud_ping=self.client.get(endpoint_ping)
        respuesta_ping=json.loads(solicitud_ping.get_data())
        mensaje=respuesta_ping["Mensaje"]
        self.assertEqual(mensaje, "Pong")

    @patch('app.verificaToken')
    def test_valida_crear_oferta(self, mock_verificaToken):
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.token)
        }

        mock_verificaToken.return_value.status_code = 200
        mock_verificaToken.return_value.json.return_value = {"id":1, "username": "Padilla", "email": "l.padillac2@uniandes.edu.co"}

        endpoint_ofertas='/offers/'

        nueva_oferta={
            "description": "Lorem Ipsum",
            "size": "MEDIUM",
            "fragile": False,
            "offer": 200
        }
        solicitud_nueva_oferta=self.client.post(endpoint_ofertas, 
                                                data=json.dumps(nueva_oferta), 
                                                headers=headers)
        respuesta_nueva_oferta=json.loads(solicitud_nueva_oferta.get_data())
        msg=respuesta_nueva_oferta["msg"]
        self.assertEqual(solicitud_nueva_oferta.status_code, 400)
        self.assertEqual(msg, "Falta la identificacion de la Publicacion.")

        nueva_oferta={
            "postId": 1,   
            "size": "MEDIUM",
            "fragile": False,
            "offer": 200
        }
        solicitud_nueva_oferta=self.client.post(endpoint_ofertas, 
                                                data=json.dumps(nueva_oferta), 
                                                headers=headers)
        respuesta_nueva_oferta=json.loads(solicitud_nueva_oferta.get_data())
        msg=respuesta_nueva_oferta["msg"]
        self.assertEqual(solicitud_nueva_oferta.status_code, 400)
        self.assertEqual(msg, "Falta la descripcion de la Publicacion.")

        nueva_oferta={
            "postId": 1,   
            "description": "Lorem Ipsum",
            "fragile": False,
            "offer": 200
        }
        solicitud_nueva_oferta=self.client.post(endpoint_ofertas, 
                                                data=json.dumps(nueva_oferta), 
                                                headers=headers)
        respuesta_nueva_oferta=json.loads(solicitud_nueva_oferta.get_data())
        msg=respuesta_nueva_oferta["msg"]
        self.assertEqual(solicitud_nueva_oferta.status_code, 400)
        self.assertEqual(msg, "Falta la dimension del paquete.")

        nueva_oferta={
            "postId": 1,   
            "description": "Lorem Ipsum",
            "size": "MEDIUM",
            "offer": 200
        }
        solicitud_nueva_oferta=self.client.post(endpoint_ofertas, 
                                                data=json.dumps(nueva_oferta), 
                                                headers=headers)
        respuesta_nueva_oferta=json.loads(solicitud_nueva_oferta.get_data())
        msg=respuesta_nueva_oferta["msg"]
        self.assertEqual(solicitud_nueva_oferta.status_code, 400)
        self.assertEqual(msg, "Falta la condicion del paquete.")


        nueva_oferta={
            "postId": 1,   
            "description": "Lorem Ipsum",
            "size": "MEDIUM",
            "fragile": False
        }
        solicitud_nueva_oferta=self.client.post(endpoint_ofertas, 
                                                data=json.dumps(nueva_oferta), 
                                                headers=headers)
        respuesta_nueva_oferta=json.loads(solicitud_nueva_oferta.get_data())
        msg=respuesta_nueva_oferta["msg"]
        self.assertEqual(solicitud_nueva_oferta.status_code, 400)
        self.assertEqual(msg, "Falta la oferta por llevar el paquete.")

        nueva_oferta={
            "postId": -1,   
            "description": "Lorem Ipsum",
            "size": "MEDIUM",
            "fragile": False,
            "offer": 200
        }
        solicitud_nueva_oferta=self.client.post(endpoint_ofertas, 
                                                data=json.dumps(nueva_oferta), 
                                                headers=headers)
        respuesta_nueva_oferta=json.loads(solicitud_nueva_oferta.get_data())
        msg=respuesta_nueva_oferta["msg"]
        self.assertEqual(solicitud_nueva_oferta.status_code, 412)
        self.assertEqual(msg, "Id de la publicacion es invalido.")

        nueva_oferta={
            "postId": 1,   
            "description": "Lorem Ipsum",
            "size": "OTRATALLA",
            "fragile": False,
            "offer": 200
        }
        solicitud_nueva_oferta=self.client.post(endpoint_ofertas, 
                                                data=json.dumps(nueva_oferta), 
                                                headers=headers)
        respuesta_nueva_oferta=json.loads(solicitud_nueva_oferta.get_data())
        msg=respuesta_nueva_oferta["msg"]
        self.assertEqual(solicitud_nueva_oferta.status_code, 412)
        self.assertEqual(msg, "Dimension del paquete incorrecta.")

        nueva_oferta={
            "postId": 1,   
            "description": "Lorem Ipsum",
            "size": "MEDIUM",
            "fragile": False,
            "offer": -200
        }
        solicitud_nueva_oferta=self.client.post(endpoint_ofertas, 
                                                data=json.dumps(nueva_oferta), 
                                                headers=headers)
        respuesta_nueva_oferta=json.loads(solicitud_nueva_oferta.get_data())
        msg=respuesta_nueva_oferta["msg"]
        self.assertEqual(solicitud_nueva_oferta.status_code, 412)
        self.assertEqual(msg, "El valor de la oferta es invalido.")


    @patch('app.verificaToken')
    def test_acrear_oferta(self, mock_verificaToken):
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.token)
        }

        endpoint_ofertas='/offers/'

        nueva_oferta={
            "postId": 1,   
            "description": "Lorem Ipsum",
            "size": "MEDIUM",
            "fragile": False,
            "offer": 200
        }

        mock_verificaToken.return_value.status_code = 200
        mock_verificaToken.return_value.json.return_value = {"id":1, "username": "Padilla", "email": "l.padillac2@uniandes.edu.co"}
        solicitud_nueva_oferta=self.client.post(endpoint_ofertas, 
                                                data=json.dumps(nueva_oferta), 
                                                headers=headers)
        respuesta_nueva_oferta=json.loads(solicitud_nueva_oferta.get_data())
        self.offerId=int(respuesta_nueva_oferta["id"])
        self.assertEqual(solicitud_nueva_oferta.status_code, 201)
    
    @patch('app.verificaToken')
    def test_consultar_oferta(self, mock_verificaToken):
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.token)
        }
        mock_verificaToken.return_value.status_code = 200
        mock_verificaToken.return_value.json.return_value = {"id":1, "username": "Padilla", "email": "l.padillac2@uniandes.edu.co"}

        endpoint_ofertas='/offers/{}'.format(self.offerId)

        solicitud_oferta=self.client.get(endpoint_ofertas, headers=headers)
        respuesta_nueva_oferta=json.loads(solicitud_oferta.get_data())
        self.assertEqual(solicitud_oferta.status_code, 200)

    @patch('app.verificaToken')
    def test_consultar_oferta_inexistente(self, mock_verificaToken):
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.token)
        }
        mock_verificaToken.return_value.status_code = 200
        mock_verificaToken.return_value.json.return_value = {"id":1, "username": "Padilla", "email": "l.padillac2@uniandes.edu.co"}


        endpoint_ofertas='/offers/{}'.format(999)

        solicitud_oferta=self.client.get(endpoint_ofertas, headers=headers)
        respuesta_solicitud_oferta=json.loads(solicitud_oferta.get_data())
        msgError=respuesta_solicitud_oferta["Error"]
        self.assertEqual(solicitud_oferta.status_code, 404)
        self.assertEqual(msgError, "No existe oferta con ese Id")

    @patch('app.verificaToken')
    def test_consultar_oferta_idinvalido(self, mock_verificaToken):
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.token)
        }
        mock_verificaToken.return_value.status_code = 200
        mock_verificaToken.return_value.json.return_value = {"id":1, "username": "Padilla", "email": "l.padillac2@uniandes.edu.co"}

        endpoint_ofertas='/offers/a'

        solicitud_oferta=self.client.get(endpoint_ofertas, headers=headers)
        respuesta_solicitud_oferta=json.loads(solicitud_oferta.get_data())
        msgError=respuesta_solicitud_oferta["Error"]
        self.assertEqual(solicitud_oferta.status_code, 400)
        self.assertEqual(msgError, "El id de la Oferta no es un numero valido")

    #@patch('app.verificaToken')
    def test_consultar_oferta_sinauth(self):  #, mock_verificaToken
        headers={
            'Content-Type': 'application/json'
        }
        #mock_verificaToken.return_value.status_code = 400
        #mock_verificaToken.return_value.json.return_value = {}

        endpoint_ofertas='/offers/1'

        solicitud_oferta=self.client.get(endpoint_ofertas, headers=headers)
        respuesta_solicitud_oferta=json.loads(solicitud_oferta.get_data())
        msgError=respuesta_solicitud_oferta["Error"]
        self.assertEqual(solicitud_oferta.status_code, 401)
        self.assertEqual(msgError, "Token Invalido o Vencido.")

    #@patch('app.verificaToken')
    def test_consultar_oferta_sintoken(self):  #, mock_verificaToken
        headers={
            'Content-Type': 'application/json',
            'Authorization': ''
        }
        #mock_verificaToken.return_value.status_code = 400
        #mock_verificaToken.return_value.json.return_value = {}

        endpoint_ofertas='/offers/1'

        solicitud_oferta=self.client.get(endpoint_ofertas, headers=headers)
        respuesta_solicitud_oferta=json.loads(solicitud_oferta.get_data())
        msgError=respuesta_solicitud_oferta["Error"]
        self.assertEqual(solicitud_oferta.status_code, 401)
        self.assertEqual(msgError, "Token Invalido o Vencido.")

    #@patch('app.verificaToken')
    def test_consultar_oferta_cad1(self):  #, mock_verificaToken
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'noBearer'
        }
        #mock_verificaToken.return_value.status_code = 400
        #mock_verificaToken.return_value.json.return_value = {}

        endpoint_ofertas='/offers/1'

        solicitud_oferta=self.client.get(endpoint_ofertas, headers=headers)
        respuesta_solicitud_oferta=json.loads(solicitud_oferta.get_data())
        msgError=respuesta_solicitud_oferta["Error"]
        self.assertEqual(solicitud_oferta.status_code, 401)
        self.assertEqual(msgError, "Token Invalido o Vencido.")

    #@patch('app.verificaToken')
    def test_consultar_oferta_cad2(self):  #, mock_verificaToken
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'noBearer token'
        }
        #mock_verificaToken.return_value.status_code = 400
        #mock_verificaToken.return_value.json.return_value = {}

        endpoint_ofertas='/offers/1'

        solicitud_oferta=self.client.get(endpoint_ofertas, headers=headers)
        respuesta_solicitud_oferta=json.loads(solicitud_oferta.get_data())
        msgError=respuesta_solicitud_oferta["Error"]
        self.assertEqual(solicitud_oferta.status_code, 401)
        self.assertEqual(msgError, "Token Invalido o Vencido.")        

    @patch('app.verificaToken')
    def test_valida_lista_ofertas(self, mock_verificaToken):
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.token)
        }
        mock_verificaToken.return_value.status_code = 200
        mock_verificaToken.return_value.json.return_value = {"id":1, "username": "Padilla", "email": "l.padillac2@uniandes.edu.co"}

        endpoint_ofertas='/offers?post=a'
        solicitud_oferta=self.client.get(endpoint_ofertas, headers=headers)
        respuesta_solicitud_oferta=json.loads(solicitud_oferta.get_data())
        msgError=respuesta_solicitud_oferta["Error"]
        self.assertEqual(solicitud_oferta.status_code, 400)
        self.assertEqual(msgError, "El id de la publicacion no es un numero valido.")

        endpoint_ofertas='/offers?filter=tu'
        solicitud_oferta=self.client.get(endpoint_ofertas, headers=headers)
        respuesta_solicitud_oferta=json.loads(solicitud_oferta.get_data())
        msgError=respuesta_solicitud_oferta["Error"]
        self.assertEqual(solicitud_oferta.status_code, 400)
        self.assertEqual(msgError, "Valor de filtro invalido.")

        endpoint_ofertas='/offers'
        solicitud_oferta=self.client.get(endpoint_ofertas, headers=headers)
        self.assertEqual(solicitud_oferta.status_code, 200)

        endpoint_ofertas='/offers?post={}'.format(self.postId)
        solicitud_oferta=self.client.get(endpoint_ofertas, headers=headers)
        self.assertEqual(solicitud_oferta.status_code, 200)

        endpoint_ofertas='/offers?filter=me'
        solicitud_oferta=self.client.get(endpoint_ofertas, headers=headers)
        self.assertEqual(solicitud_oferta.status_code, 200)

        endpoint_ofertas='/offers?post={}&filter=me'.format(self.postId)
        solicitud_oferta=self.client.get(endpoint_ofertas, headers=headers)
        self.assertEqual(solicitud_oferta.status_code, 200)

