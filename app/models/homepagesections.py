# models/homepage_section.py

from app.extensions import db

class HomepageSection(db.Model):
    __tablename__ = 'homepage_sections'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    section_type = db.Column(db.String(50), nullable=False)  # e.g., 'intervention', 'product'

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "image_url": self.image_url,
            "section_type": self.section_type
        }
