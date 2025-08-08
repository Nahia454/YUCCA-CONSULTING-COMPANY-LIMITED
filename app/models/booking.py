from datetime import datetime
from app.extensions import db

class Booking(db.Model):
    __tablename__ = "bookings"
    booking_id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.farmer_id'), nullable=True)  # nullable if not always needed
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    status = db.Column(db.String(50), default="pending")
    verification_code = db.Column(db.String(6), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    preferred_date = db.Column(db.Date, nullable=False)
    guest_name = db.Column(db.String(100), nullable=True)
    guest_contact = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    farmer = db.relationship('Farmer', backref='bookings')
    user = db.relationship('User', backref='bookings')
    service = db.relationship('Service', backref='bookings')


