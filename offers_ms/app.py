from flask_restful import Api
from flask_jwt_extended import JWTManager
import os
import requests
from flask import Flask, make_response

app=Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("POSTGRES_URL") #'postgresql://admin:admin@localhost:5432/OffersDB'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv("SECRET_KEY")  
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = True

ambiente=os.getenv("AMBIENTE")
if ambiente=='pruebas':
   app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("POSTGRES_URL")
if ambiente=='local':
   #app.config['JWT_SECRET_KEY'] = 'not-enough-secret'
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost:5432/OffersDB'  
if ambiente=="produccion":
   app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("POSTGRES_URL") 

app_context=app.app_context()
app_context.push()


import enum
from sqlalchemy import DateTime
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from sqlalchemy.sql import func
from sqlalchemy import Date

db = SQLAlchemy()

class Size(enum.Enum):
    LARGE = 1
    MEDIUM = 2
    SMALL = 3

class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    postId = db.Column(db.Integer, nullable=False)
    userId = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Unicode(140))
    size = db.Column(db.Enum(Size), nullable=False, default=Size.SMALL)
    fragile = db.Column(db.Boolean, default=False)
    offer = db.Column(db.Float, nullable=False)
    createdAt = db.Column(Date(), nullable=False, default=func.now())
    
class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        else:
            return value.name #{'llave':value.name, 'valor':value.value} #{value.name}  #{'llave':value.name, 'valor':value.value}
    
class OfferSchema(SQLAlchemyAutoSchema):
    size=EnumADiccionario(attribute=('size'))
    class Meta:
        model = Offer
        include_relationships = True
        load_instance = True


db.init_app(app)
db.create_all()


import os
import shutil
from datetime import datetime
from flask import request, send_file
from flask_restful import Resource
from werkzeug.utils import secure_filename

from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError
from functools import wraps
from jwt import InvalidSignatureError, ExpiredSignatureError, InvalidTokenError

offer_schema = OfferSchema()
ALLOWED_SIZE = {'LARGE', 'MEDIUM', 'SMALL'}

def verificaToken(headers):
   if not "Authorization" in headers:
      return make_response({"Error":"Missing Authorization."}, 401) 
   cad=request.headers["Authorization"]
   if cad is None or not cad:
 
      return make_response({"Error":"Missing Authorization."}, 401) 
   else:
      lst=cad.split()
      if len(lst)<2:
         return make_response({"Error":"Cadena Incorrecta."}, 401) 
      else:
         if lst[0]!='Bearer':
            return make_response({"Error":"Cadena Incorrecta."}, 401) 
         else:
            req_headers={"Authorization": f"Bearer {lst[1]}"}
            r=requests.get("http://127.0.0.1:5000/users/me", headers=req_headers)
            #r=requests.get("http://users-ms:5000/users/me", headers=req_headers)
            #r=requests.get(f"http://{os.environ['USERS_MS']}/users/me", headers=req_headers)
            return r

class VistaOffer(Resource):
    def post(self):
        respUsers=verificaToken(request.headers)
        if respUsers.status_code!=200:
            return {"Error": "Token Invalido o Vencido."}, 401
        datos=respUsers.json()

        user_jwt=int(datos["id"])
        postId=request.json.get('postId')
        if postId is None:
           return {"msg":"Falta la identificacion de la Publicacion."}, 400
        description=request.json.get('description')
        if description is None:
           return {"msg":"Falta la descripcion de la Publicacion."}, 400
        size=request.json.get('size')
        if size is None:
           return {"msg":"Falta la dimension del paquete."}, 400
        fragile=request.json.get('fragile')
        if fragile is None:
           return {"msg":"Falta la condicion del paquete."}, 400
        offer=request.json.get('offer')   
        if offer is None:
           return {"msg":"Falta la oferta por llevar el paquete."}, 400
      
        if postId<0:
           return {"msg":"Id de la publicacion es invalido."}, 412
        if not(size=='LARGE' or size=='MEDIUM' or size=='SMALL'):
           return {"msg":"Dimension del paquete incorrecta."}, 412
        if offer<=0:
           return {"msg":"El valor de la oferta es invalido."}, 412
        
        nueva_oferta=Offer(userId=user_jwt, postId=postId, description=description, size=Size[size], fragile=fragile, offer=offer, createdAt=datetime.now())
        db.session.add(nueva_oferta)
        db.session.commit()
        return {"id":nueva_oferta.id, "userId":nueva_oferta.userId, "createdAt": nueva_oferta.createdAt.isoformat()}, 201

class VistaOfferList(Resource):
    def get(self):
       respUsers=verificaToken(request.headers)
       if respUsers.status_code!=200:
           return {"Error": "Token Invalido o Vencido."}, 401
       datos=respUsers.json()

       user_jwt=int(datos["id"])
       postIdTemp=request.args.get("post")
       if postIdTemp is not None:
          try:
             postId=int(postIdTemp)
          except Exception as inst:
             return {"Error": "El id de la publicacion no es un numero valido."}, 400

       filter = request.args.get("filter")
       if filter!=None and filter!='me':
          return {"Error": "Valor de filtro invalido."}, 400
       #if filter==None:
       #   return {"Error:": "Parametro filtro es obligatorio"}, 400

       if filter is not None and postIdTemp is not None:
          return  [offer_schema.dump(offer) for offer in Offer.query.filter(Offer.postId==postId, Offer.userId==user_jwt).all()], 200   #.filter(Offer.postId==postId, Offer.userId==user_jwt).all()
       elif filter is not None:
          return  [offer_schema.dump(offer) for offer in Offer.query.filter(Offer.userId==user_jwt).all()], 200 
       elif postIdTemp is not None:
          return  [offer_schema.dump(offer) for offer in Offer.query.filter(Offer.postId==postId).all()], 200           
       else:
          return  [offer_schema.dump(offer) for offer in Offer.query], 200

class VistaGetOffer(Resource):
    def get(self, id):
        respUsers=verificaToken(request.headers)
        if respUsers.status_code!=200:
            return {"Error": "Token Invalido o Vencido."}, 401
        datos=respUsers.json()

        user_jwt=int(datos["id"])
        try:
           offerId=int(id)
        except Exception as inst:
           return {"Error": "El id de la Oferta no es un numero valido"}, 400

        #offer=Offer.query.get_or_404(id)
        offer=Offer.query.get(offerId)
        if offer is None:
           return {"Error": "No existe oferta con ese Id"}, 404
        return {
          "id": offer.id , 
          "postId": offer.postId, 
          "userId": offer.userId, 
          "description": offer.description, 
          "size": offer.size.name, 
          "fragile" : offer.fragile, 
          "offer": offer.offer, 
          "createdAt": offer.createdAt.isoformat()
        }, 200   
        # offer_schema.dump(offer), 200

class VistaPing(Resource):
    def get(self):
        print("pong")
        return {"Mensaje":"Pong"}, 200


api = Api(app)
api.add_resource(VistaOffer, '/offers/')
api.add_resource(VistaOfferList, '/offers', endpoint='offers')
api.add_resource(VistaGetOffer, '/offers/<id>')
api.add_resource(VistaPing, '/offers/ping')


jwt = JWTManager(app)