from offers_ms.modelos.modelos import db, Offer, OfferSchema, Size
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

def authorization_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()    
                user_jwt=str(int(get_jwt_identity()))
                print(user_jwt) 
                return fn(*args, **kwargs)
            except ExpiredSignatureError:
                return {"Error:": "Token Expired"}, 401
            except InvalidSignatureError:
                return {"Error:": "Signature verification failed"}, 401
            except NoAuthorizationError:
                return {"Error:": "Missing JWT"}, 401
            except Exception as inst:
                print("excepcion")
                print(type(inst))    # the exception instance
                print(inst)
                return {"Error:": "Usuario Desautorizado"}, 401
        return decorator
    return wrapper

def authorization2_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                lstTokens=request.path.split(sep='/')    
                print(lstTokens)
                lstTokens[len(lstTokens)-1]
                print(lstTokens[len(lstTokens)-1])
                ##user_url=request.path[-1:]  ##generalizar a un numero de dos y mas cifras
                user_url=lstTokens[len(lstTokens)-1]
                print(user_url)
                verify_jwt_in_request()  
                try:
                   offerId=int(user_url)
                   return fn(*args, **kwargs)
                except Exception as inst:
                   return {"Error:": "El id de la Oferta no es un numero valido"}, 401
            except ExpiredSignatureError:
                return {"Error:": "Token Expired"}, 401
            except InvalidSignatureError:
                return {"Error:": "Signature verification failed"}, 401
            except NoAuthorizationError:
                return {"Error:": "Missing JWT"}, 401
            except Exception as inst:
                print("excepcion")
                print(type(inst))    # the exception instance
                print(inst)
                return {"Error:": "Usuario Desautorizado"}, 401
        return decorator
    return wrapper

class VistaOffer(Resource):
    @authorization_required()
    def post(self):
        print("Creacion")
        user_jwt=str(int(get_jwt_identity()))
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

    @authorization_required()
    def get(self):
       print("la otra")
       user_jwt=int(get_jwt_identity())
       postIdTemp=request.args.get("post")
       if postIdTemp is not None:
          try:
             postId=int(postIdTemp)
          except Exception as inst:
             print(type(inst))    # the exception instance
             return {"Error:": "El id de la publicacion no es un numero valido"}, 400

       print("Despues parametros")
       filter = request.args.get("filter")
       if filter!=None and filter!='me':
          return {"Error:": "Valor de filtro invalido"}, 400
       #if filter==None:
       #   return {"Error:": "Parametro filtro es obligatorio"}, 400

       print("Despues me")
       if filter is not None and postIdTemp is not None:
          print("Despues ambos")
          return  [offer_schema.dump(offer) for offer in Offer.query.filter(Offer.postId==postId, Offer.userId==user_jwt).all()]   #.filter(Offer.postId==postId, Offer.userId==user_jwt).all()
       elif filter is not None:
          print("Despues filrter")
          return  [offer_schema.dump(offer) for offer in Offer.query.filter(Offer.userId==user_jwt).all()] 
       elif postIdTemp is not None:
          print("Despues postId")
          return  [offer_schema.dump(offer) for offer in Offer.query.filter(Offer.postId==postId).all()]           
       else:
          print("Despues else")
          return  [offer_schema.dump(offer) for offer in Offer.query] 

class VistaGetOffer(Resource):
    @authorization_required()
    def get(self, id):
        print("Consulta")
        try:
           offerId=int(id)
        except Exception as inst:
           return {"Error:": "El id de la Oferta no es un numero valido"}, 400

        #offer=Offer.query.get_or_404(id)
        offer=Offer.query.get(offerId)
        if offer is None:
           return {"Error:": "No existe oferta con ese Id"}, 404
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
