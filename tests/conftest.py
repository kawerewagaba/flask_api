import pytest
from app import app
from flask_sqlalchemy import SQLAlchemy

# local imports
from instance.config import app_config

@pytest.fixture
def app_fixture():
    # overriding config
    app.config.from_object(app_config['testing'])

    """
    operating within the application context
    helps in this case because we shall not be sending actual requests from the browser
    """
    with app.app_context():
        # create all tables
        db = SQLAlchemy(app)
        db.create_all()

@pytest.fixture
def client(app_fixture):
    client = app.test_client()
    return client
