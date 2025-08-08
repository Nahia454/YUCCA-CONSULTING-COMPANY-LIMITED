from datetime import datetime
from app.extensions import db



class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    contact = db.Column(db.String(100))
    message = db.Column(db.Text)
    reply = db.Column(db.Text, nullable=True)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)