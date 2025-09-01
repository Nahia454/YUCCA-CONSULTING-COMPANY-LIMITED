from datetime import datetime
from app.extensions import db


# --- INTRO SECTION (Hero with text + background image) ---
class HomeIntro(db.Model):
    __tablename__ = "home_intro"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    text = db.Column(db.Text, nullable=True)   # <-- frontend expects this
    image = db.Column(db.String(255))          # hero image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# --- PRODUCTS SECTION ---
class HomeProduct(db.Model):
    __tablename__ = "home_products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255))  # product image path
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# --- PARTNERS SECTION ---
class HomePartner(db.Model):
    __tablename__ = "home_partners"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    logo = db.Column(db.String(255))  # partner logo path
    link = db.Column(db.String(255))  # website link (optional)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# --- INTERVENTIONS SECTION ---
class HomeIntervention(db.Model):
    __tablename__ = "home_interventions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))  # intervention image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

 # ------------------- DEALERS SECTION -------------------
class HomeDealer(db.Model):
    __tablename__ = "home_dealers"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
   
