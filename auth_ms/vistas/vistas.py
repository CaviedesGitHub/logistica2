from datetime import datetime
from datetime import timedelta
import uuid
from flask import request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from flask_login import (current_user, login_user, logout_user, login_required)
from auth_ms.modelos.modelos import db, Usuario, UsuarioSchema

usuario_schema = UsuarioSchema()

access_token_expires = timedelta(minutes=120)

class VistaSignIn(Resource):   
    def post(self):
        print('VistaSignIn')
        username=request.json.get('username')
        email=request.json.get('email')
        password=request.json.get('password')
        if username==None or email==None or password==None:
           return {"mensaje": "Falta(n) uno o mas campos en la peticion"}, 400
        else:
           usuario=Usuario.query.filter(Usuario.email == request.json["email"]).first() 
           if usuario is None:
              usuario=Usuario.query.filter(Usuario.username == request.json["username"]).first() 
              if usuario is None:
                 nuevo_usuario = Usuario(username=request.json["username"], email=request.json["email"])
                 nuevo_usuario.salt = str(uuid.uuid4())
                 nuevo_usuario.set_password(request.json["password"]+nuevo_usuario.salt) 
                 nuevo_usuario.expireAt=datetime.now()
                 nuevo_usuario.createdAt=datetime.now()
                 db.session.add(nuevo_usuario)
                 db.session.commit()
                 #nuevo_usuario.expireAt=datetime.utcnow() + timedelta(minutes = access_token_expires)
                 #token_de_acceso = create_access_token(identity=nuevo_usuario.id, expires_delta=access_token_expires)
                 #nuevo_usuario.token=token_de_acceso
                 #db.session.add(nuevo_usuario)
                 #db.session.commit()
                 return {"id": nuevo_usuario.id, "createdAt": nuevo_usuario.createdAt.isoformat()}, 201
              else:
                 return {"mensaje": "username ya existe."}, 412  
           else:
              return {"mensaje": "email ya existe."}, 412

class VistaLogIn(Resource):
    def post(self):
        if request.json.get('username')==None or request.json.get('password')==None:
           return {"mensaje": "Falta(n) uno o mas campos en la peticion"}, 400
        else:
           usuario = Usuario.query.filter(Usuario.username == request.json["username"]).first()
           if usuario is not None:
              db.session.commit()
              if usuario.authenticate(request.json["password"]+usuario.salt):
                 login_user(usuario)
                 print(type(usuario.expireAt))
                 print(usuario.expireAt)
                 print(type(datetime.now()))
                 print(datetime.now())
                 if usuario.expireAt>datetime.now():
                    return {"idaa":usuario.id, "token":usuario.token, "expireAt":usuario.expireAt.isoformat()}, 200
                 else:
                    usuario.expireAt=datetime.now() + timedelta(minutes = 120)
                    token_de_acceso = create_access_token(identity=usuario.id, expires_delta=access_token_expires)
                    usuario.token=token_de_acceso
                    db.session.add(usuario)
                    db.session.commit()
                    return {"idbb":usuario.id, "token":usuario.token, "expireAt":usuario.expireAt.isoformat()}, 200
              else:
                 return {"mensaje":"LogIn Incorrecto."}, 404
           else:
              return {"mensaje":"LogIn Incorrecto."}, 404

class VistaLogOut(Resource):
    def post(self):
        logout_user()
        return {"mensaje":"LogOut Exitoso."}

class VistaUser(Resource):
    def get(self):
        return {}, 200

class VistaUsuario(Resource):   
    def get(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        return usuario_schema.dump(usuario)

    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        if request.json.get("password") is not None:
           usuario.set_password(request.json["password"])
        usuario.name=request.json.get("name", usuario.name)
        usuario.email=request.json.get("email", usuario.email)
        if request.json.get("is_admin") is not None:
           usuario.is_admin=eval(request.json.get("is_admin"))
        db.session.commit()
        return usuario_schema.dump(usuario)

    def delete(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return "Usuario Borrado.",  204

class VistaUsuarios(Resource):   
   @jwt_required()     
   def get(self):
       user_jwt=int(get_jwt_identity())  
       if current_user.is_authenticated:  ##current_user.get_id() is not None:
            if current_user.get_id()==user_jwt:  
                if current_user.is_admin:
                    return [usuario_schema.dump(user) for user in Usuario.query] 
       return  {"Msg":"Usuario desautorizado."}

class VistaPing(Resource):
    def get(self):
        print("pong")
        return {"Mensaje":"Pong"}, 200