from datetime import datetime
from app.extensions import db

class Farmer(db.Model):
    __tablename__ = "farmers"
    farmer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True) 
    name = db.Column(db.String(50))
    location = db.Column(db.String(100))
    crops_grown = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)
    user = db.relationship('User', backref='farmers')