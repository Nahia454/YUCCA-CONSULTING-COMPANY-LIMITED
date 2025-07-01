from flask import Flask





# Apllication Function factory: it builds and returns an instance of a Flask application
def create_app():  # This is an application factory
    app = Flask(__name__)  # Initialize the Flask app
    app.config.from_object('config.Config')  # registering the database










# register blueprints


    
   # migrations are always in order

    # Define routes
    @app.route("/")
    def home():
       return "Author's API setup"

    return app  # Return the app instance

# Only run the app if this script is executed directly
if  __name__ == '__main__':
  
    app = create_app()
    app.run(debug=True)  # Run the app
