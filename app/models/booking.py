from datetime import datetime
from app.extensions import db

class Booking(db.Model):
    __tablename__ = "bookings"
    booking_id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    status = db.Column(db.String(50), default="pending")
    verification_code = db.Column(db.String(6), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    preferred_date = db.Column(db.Date, nullable=False)
    guest_name = db.Column(db.String(100), nullable=True)
    guest_contact = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

  
    service = db.relationship('Service', backref='bookings')


# # app/models/booking.py
# from datetime import datetime, timedelta
# from app.extensions import db
# import uuid

# class Booking(db.Model):
#     __tablename__ = "bookings"

#     booking_id = db.Column(db.Integer, primary_key=True)  # internal ID
#     guest_name = db.Column(db.String(100), nullable=False)
#     guest_contact = db.Column(db.String(100), nullable=False)
#     service_id = db.Column(db.Integer, db.ForeignKey("services.service_id"), nullable=False)
#     preferred_date = db.Column(db.Date, nullable=False)

#     status = db.Column(
#         db.String(20), default="pending"
#     )  # pending, confirmed, expired
#     is_verified = db.Column(db.Boolean, default=False)

#     reference_code = db.Column(
#     db.String(20), unique=True, nullable=False, default=lambda: str(uuid.uuid4())[:8])

#     # default is 8-character unique code, used for payment verification

#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))
#     paid_at = db.Column(db.DateTime, nullable=True)

#     service = db.relationship("Service", backref="bookings")

#     def mark_expired(self):
#         """Mark booking as expired if past expiry time"""
#         if self.status == "pending" and datetime.utcnow() > self.expires_at:
#             self.status = "expired"
#             self.is_verified = False


