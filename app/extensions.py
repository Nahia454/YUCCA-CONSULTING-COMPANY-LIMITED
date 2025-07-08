from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


#the instance
db = SQLAlchemy()
migrate = Migrate()