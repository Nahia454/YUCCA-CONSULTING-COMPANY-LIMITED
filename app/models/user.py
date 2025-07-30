from datetime import datetime
from app.extensions import db

class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    contact = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    def __init__(self, first_name, last_name, email, contact, password, user_type):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.contact = contact
        self.password = password
        self.user_type = user_type

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "contact": self.contact,
            "user_type": self.user_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
