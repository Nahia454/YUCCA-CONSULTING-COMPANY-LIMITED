from datetime import datetime
from app.extensions import db

class Product(db.Model):
    __tablename__ = "products"
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50)) 
    image = db.Column(db.String(255))  # will store full URL, not just filename
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name, category=None, image=None):
        self.name = name
        self.category = category
        self.image = image

    def as_dict(self):
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "image": self.image,  # frontend will get URL
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class ProductBanner(db.Model):
    __tablename__ = "product_banners"
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)

    def as_dict(self):
        return {"id": self.id, "image_url": self.image_url}
