# models/homepage_media.py

from app.extensions import db

class HomepageMedia(db.Model):
    __tablename__ = 'homepage_media'
    id = db.Column(db.Integer, primary_key=True)
    media_type = db.Column(db.String(50), nullable=False)  # e.g., 'partner_logo'
    image_url = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "media_type": self.media_type,
            "image_url": self.image_url
        }
