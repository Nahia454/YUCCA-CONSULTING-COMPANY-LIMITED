from flask import Flask
from app.extensions import db, migrate






def create_app():  # This is an application factory
    app = Flask(__name__)  # Initialize the Flask app
    app.config.from_object('config.Config')  # registering the database

    db.init_app(app)         # initializing db with app
    migrate.init_app(app, db)  # initializing migration with app and db


    
    # import the models  
    from app.models.booking import Booking
    from app.models.farmer import Farmer
    from app.models.feedback import Feedback
    from app.models.order import Order
    from app.models.product import Product
    from app.models.service import Service
    from app.models.user import User

    
    

    

    # Define routes
    @app.route("/")
    def home():
       return "Yucca's  API setup"

    return app  # Return the app instance


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)  # Run the app
