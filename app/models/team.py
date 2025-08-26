from app.extensions import db

class TeamMember(db.Model):
    __tablename__ = "team_members"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=True)  # URL/path to uploaded image
    twitter = db.Column(db.String(200), nullable=True)  # Former Twitter link
    linkedin = db.Column(db.String(255), nullable=True)
