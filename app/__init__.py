from flask import Flask
from app.extensions import db, migrate, jwt, bcrypt, cors

# Import blueprints
from app.controllers.auth_controller import auth
from app.controllers.users.user_controller import users
from app.controllers.services.service_controller import services
from app.controllers.farmer.farmer_controller import farmers
from app.controllers.booking.booking_controller import bookings
from app.controllers.product_controller import products
from app.controllers.feedback_controller import feedbacks
from app.controllers.admin.admin_controller import admin
from app.controllers.admin.admin_controller import auth_bp

# Import models to register them with SQLAlchemy
from app.models.user import User
from app.models.service import Service
from app.models.product import Product
from app.models.booking import Booking
from app.models.feedback import Feedback
from app.models.farmer import Farmer

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # Or any config file you use

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, supports_credentials=True)
    jwt.init_app(app)
    bcrypt.init_app(app)


    # JWT secret key
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # change in production

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(services)
    app.register_blueprint(farmers)
    app.register_blueprint(bookings)
    app.register_blueprint(products)
    app.register_blueprint(feedbacks)
    app.register_blueprint(admin)
    app.register_blueprint(auth_bp)

    # Default route
    @app.route("/")
    def home():
        return "Welcome to Yucca Consulting Limited API"

    return app
