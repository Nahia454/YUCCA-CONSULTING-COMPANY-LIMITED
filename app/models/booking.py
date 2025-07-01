from app.extensions import db
from datetime import datetime

class Booking(db.Model):
    __tablename__= "bookings"
    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'))
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime,default = datetime.now())
    updated_at = db.Column(db.DateTime, onupdate = datetime.now())

    user = db.relationship('User', backref='bookings')
    service = db.relationship('Service', backref='bookings')