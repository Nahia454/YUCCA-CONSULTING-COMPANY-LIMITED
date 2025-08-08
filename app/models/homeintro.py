# models/home_intro.py

from app.extensions import db

class HomeIntro(db.Model):
    __tablename__ = 'home_intro'
    id = db.Column(db.Integer, primary_key=True)
    hero_text = db.Column(db.String(255), nullable=False)
    intro_title = db.Column(db.String(255), nullable=False)
    intro_description = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "hero_text": self.hero_text,
            "intro_title": self.intro_title,
            "intro_description": self.intro_description
        }
