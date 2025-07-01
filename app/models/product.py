from app.extensions import db
from datetime import datetime


class Product(db.Model):
    __tablename__= "products"
    product_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    quantity = db.Column(db.Integer)
    subtotal = db.Column(db.Float)
    order = db.relationship('Order', backref='products')
    service = db.relationship('Service', backref='products')
    created_at = db.Column(db.DateTime,defult = datetime.now())
    updated_at = db.Column(db.DateTime, onupdate = datetime.now())

    def __init__(self,quantity,subtotal):
        self.quantity = quantity
        self.subtotal = subtotal