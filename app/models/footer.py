from datetime import datetime
from app.extensions import db

class Footer(db.Model):
    __tablename__ = "footers"
    id = db.Column(db.Integer, primary_key=True)
    
    # Quick Links
    link_name = db.Column(db.String(100), nullable=False)
    link_url = db.Column(db.String(255), nullable=False)
    
    # Contact Info
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(255))
    
    # Social Media
    facebook = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    linkedin = db.Column(db.String(255))
    instagram = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "link_name": self.link_name,
            "link_url": self.link_url,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "facebook": self.facebook,
            "twitter": self.twitter,
            "linkedin": self.linkedin,
            "instagram": self.instagram
        }
