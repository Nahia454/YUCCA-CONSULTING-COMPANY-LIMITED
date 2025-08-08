# from datetime import datetime
# from app.extensions import db

# class Feedback(db.Model):
#     __tablename__ = "feedbacks"
#     feedback_id = db.Column(db.Integer, primary_key=True)
#     service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
#     rating = db.Column(db.Integer)
#     comment = db.Column(db.String(255))
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     service = db.relationship('Service', backref='feedbacks')

from datetime import datetime
from app.extensions import db

class Feedback(db.Model):
    __tablename__ = "feedbacks"
    feedback_id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.farmer_id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable= True)
    comment = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    farmer = db.relationship('Farmer', backref='feedbacks')
    service = db.relationship('Service', backref='feedbacks')
    user = db.relationship('User',backref = 'feedbacks')
