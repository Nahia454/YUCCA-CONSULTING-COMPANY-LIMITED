from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.extensions import db, migrate, bcrypt, jwt
from flask_jwt_extended import JWTManager
from app.controllers.auth_controller import auth
from app.controllers.users.user_controller import users
from app.controllers.services.service_controller import services
from app.controllers.farmer.farmer_controller import farmers
from app.controllers.booking.booking_controller import bookings
from app.controllers.feedback.feedback_controller import feedback






#  Apllication Function factory: it builds and returns an instance of a Flask application
def create_app():  # This is an application factory
    app = Flask(__name__) # Initialize the Flask app
    app.config.from_object('config.Config')  # registering the database


    db.init_app(app) 
    migrate.init_app(app, db) 
    jwt.init_app(app)
    bcrypt.init_app(app)

    app.config['JWT_SECRET_KEY'] = 'HS256'
    


    from app.models.user import User
    from app.models.service import Service
    from app.models.booking import Booking
    from app.models.feedback import Feedback
    from app.models.farmer import Farmer
    


 
# register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(services)
    app.register_blueprint(farmers)
    app.register_blueprint(bookings)
    app.register_blueprint(feedback)


    
   # migrations are always in order

    # Define routes
    @app.route("/")
    def home():
       return "Yucca Consulting Limited"

    return app  # Return the app instance


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)  # Run the app
