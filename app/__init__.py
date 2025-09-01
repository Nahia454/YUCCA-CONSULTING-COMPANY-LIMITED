from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

from app.extensions import db, migrate, jwt, bcrypt, mail
from flask_cors import CORS
# Import blueprints
from app.controllers.auth_controller import auth
from app.controllers.users.user_controller import users
from app.controllers.services.service_controller import services
from app.controllers.farmer.farmer_controller import farmers
from app.controllers.booking.booking_controller import bookings
from app.controllers.product_controller import products
from app.controllers.feedback_controller import feedback
from app.controllers.admin.admin_controller import admin
from app.controllers.contact_controller import contact
from app.controllers.dash_controller import dashboard
from app.controllers.home.homepage_controller import homepage
from app.controllers.about_controller import about
from app.controllers.footer_controller import footer
from app.controllers.team_controller import team

# Import models (so SQLAlchemy recognizes them)
from app.models.user import User
from app.models.service import Service
from app.models.product import Product,ProductBanner
from app.models.booking import Booking
from app.models.feedback import Feedback
from app.models.farmer import Farmer
from app.models.contact import ContactMessage,ContactBanner
from app.models.homepage import HomeIntro, HomeProduct, HomePartner, HomeIntervention,HomeDealer
from app.models.footer import Footer
from app.models.team import TeamMember



def create_app():
    app = Flask(__name__)
    

    # Load configs from .env
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Mail config
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')


    # JWT secret key
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # 🔒 Change this in production

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    # cors.init_app(app, supports_credentials=True)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    # Register all blueprints
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(services)
    app.register_blueprint(farmers)
    app.register_blueprint(bookings)
    app.register_blueprint(products)
    app.register_blueprint(feedback)
    app.register_blueprint(admin)
    app.register_blueprint(contact)
    app.register_blueprint(dashboard)
    app.register_blueprint(homepage)
    app.register_blueprint(about)
    app.register_blueprint(footer)
    app.register_blueprint(team)

    # Default route
    @app.route("/")
    def home():
        return "Welcome to Yucca Consulting Limited API"

    return app