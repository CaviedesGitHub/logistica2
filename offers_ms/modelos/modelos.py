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