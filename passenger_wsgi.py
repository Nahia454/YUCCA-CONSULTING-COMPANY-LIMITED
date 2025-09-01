import sys 

# locate the root of your project
import os 

# Path to your project
project_home = os.path.dirname(_file_)
if project_home not in sys.path:
	sys.path.insert(0, project_home)
 
 
 
# Import your factory and create the app
from app import create_app
application = create_app() # Passenger needs this "application"