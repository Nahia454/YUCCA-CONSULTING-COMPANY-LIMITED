# models/home_intro.py

from app.extensions import db

class HomeIntro(db.Model):
    __tablename__ = 'home_intro'
    id = db.Column(db.Integer, primary_key=True)
    hero_text = db.Column(db.String(255), nullable=False)
    intro_title = db.Column(db.String(255), nullable=False)
    intro_description = db.Column(db.Text, nullable=False)



def __init__(self, hero_text, intro_title=None, intro_description=None):
    self.hero_text = hero_text
    self.intro_title = intro_title
    self.intro_description = intro_description


    # def to_dict(self):
    #     return {
    #         "id": self.id,
    #         "hero_text": self.hero_text,
    #         "intro_intro_title": self.intro_title,
    #         "intro_intro_description": self.intro_description
    #     }
