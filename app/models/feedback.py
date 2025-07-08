from app.extensions import db
from datetime import datetime

class Feedback(db.Model):
    __tablename__= "feedbacks"
    feedback_id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.farmer_id'))
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.String(255))
    created_at = db.Column(db.DateTime,default = datetime.now())
    updated_at = db.Column(db.DateTime, onupdate = datetime.now())

    farmer = db.relationship('Farmer', backref='feedbacks')
    service = db.relationship('Service', backref='feedbacks')