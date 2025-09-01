from datetime import datetime
from app.extensions import db



class ContactMessage(db.Model):
    __tablename__ = "contact_messages"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text)
    subject = db.Column(db.String(150), nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    def as_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "subject": self.subject,
            "message": self.message,
            "created_at": self.created_at.isoformat()  # JSON-safe
        }


# app/models/contact.py

class ContactBanner(db.Model):
    __tablename__ = "banners"
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
