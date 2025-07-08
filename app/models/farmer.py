from app.extensions import db
from datetime import datetime

class Farmer(db.Model):
    __tablename__ = "farmers"  
    farmer_id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100))
    farm_size = db.Column(db.String(50))
    crops_grown = db.Column(db.String(200))
    created_at = db.Column(db.DateTime,defult = datetime.now())
    updated_at = db.Column(db.DateTime, onupdate = datetime.now())