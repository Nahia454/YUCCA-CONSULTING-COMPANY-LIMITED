from app.extensions import db
from datetime import datetime

class Service(db.Model):
    __tablename__= "services"
    service_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime,default = datetime.now())
    updated_at = db.Column(db.DateTime, onupdate = datetime.now())

    def __init__(self,name,description,price,category):
        self.name = name
        self.description = description
        self.price = price
        self.category = category