from app.extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__= "orders"
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    order_date = db.Column(db.Date)
    totalamount = db.Column(db.Float)
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime,defult = datetime.now())
    updated_at = db.Column(db.DateTime, onupdate = datetime.now())

    user = db.relationship('User', backref='orders')

    def __init__(self,order_date,total):
        self.order_date = order_date
        self.total = total