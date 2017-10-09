import pytest # importing the testing framework
import json
from app import app, db

# local imports
from instance.config import app_config

@pytest.fixture
def setup():
    # overriding config
    app.config.from_object(app_config['testing'])
    client = app.test_client
    # mock data
    bucketlist = {'name': 'Career'}

    """
    operating within the application context
    helps in this case because we shall not be sending actual requests from the browser
    """
    with app.app_context():
        # create all tables
        db.create_all()

def test_create_bucketlist(setup):
    """
    Test API can create a bucketlist (POST request)
    """
    response = client.post('/bucketlists/', data=bucketlist)
    assert response.status_code == 201
    assert 'Career' in response.data
