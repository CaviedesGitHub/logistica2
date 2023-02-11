from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_login import UserMixin
from sqlalchemy import DateTime, Date
from sqlalchemy.sql import func

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Unicode(128), nullable=False, unique=True)
    email = db.Column(db.Unicode(128), nullable=False, unique=True)
    password = db.Column(db.Unicode(128))
    salt = db.Column(db.Unicode(128))
    token = db.Column(db.Unicode(512))
    expireAt = db.Column(DateTime(timezone=False), nullable=False, default=func.now())
    createdAt = db.Column(Date(), nullable=False, default=func.now)

    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kw):
        super(Usuario, self).__init__(*args, **kw)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        return checked

    def get_id(self):
        return self.id

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Usuario.query.get(id)

    @staticmethod
    def get_by_email(email):
        return Usuario.query.filter_by(email=email).first()
    
class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True

usuario_schema = UsuarioSchema()
