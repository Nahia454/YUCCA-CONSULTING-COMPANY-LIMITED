from app import db
from datetime import datetime

class About(db.Model):
    __tablename__ = 'about_page'

    id = db.Column(db.Integer, primary_key=True)

    # Intro
    intro_text = db.Column(db.Text, nullable=True)
    intro_image = db.Column(db.String(255), nullable=True)

    # Vision & Mission
    vision_title = db.Column(db.String(255), nullable=True)
    vision_text = db.Column(db.Text, nullable=True)
    mission_title = db.Column(db.String(255), nullable=True)
    mission_text = db.Column(db.Text, nullable=True)

    # Values
    values_title = db.Column(db.String(255), nullable=True)
    values_list = db.Column(db.Text, nullable=True)  # store each value separated by newline
    values_image = db.Column(db.String(255), nullable=True)

    # Expertise
    expertise_title = db.Column(db.String(255), nullable=True)
    expertise_intro = db.Column(db.Text, nullable=True)
    expertise_list = db.Column(db.Text, nullable=True)  # store each item separated by newline
    expertise_image = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
