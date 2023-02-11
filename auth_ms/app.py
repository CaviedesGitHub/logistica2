from auth_ms import create_app
from auth_ms.vistas.vistas import VistaUsuario, VistaLogIn, VistaSignIn, VistaPing, VistaUsuarios, VistaLogOut
from auth_ms.modelos.modelos import db, Usuario
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_login import LoginManager

app=create_app('default')
app_context=app.app_context()
app_context.push()

db.init_app(app)
db.create_all()


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.get_by_id(int(user_id))


api = Api(app)
api.add_resource(VistaSignIn, '/users/')
api.add_resource(VistaLogIn, '/users/auth')
#api.add_resource(VistaLogOut, '/users/auth/logout')
#api.add_resource(VistaUsuario, '/usuario/<int:id_usuario>')
#api.add_resource(VistaUsuarios, '/usuarios')
api.add_resource(VistaPing, '/users/ping')


jwt = JWTManager(app)
