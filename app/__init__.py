# third-party imports
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# local imports
from instance.config import app_config

app = FlaskAPI(__name__, instance_relative_config = True)
app.config.from_object(app_config['development'])
app.config.from_pyfile('config.py')

# db variable initialization
db = SQLAlchemy(app)

# Load the views
from app import views
