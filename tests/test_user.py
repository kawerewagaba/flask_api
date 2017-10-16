# adding the parent directory when searching for modules
import sys
sys.path.append('../')
# still fails when called outside parent directory

import unittest
import json

from app import create_app, db
from flask_bcrypt import Bcrypt

class UserTestCase(unittest.TestCase):
    """This class represents the user test case"""

    def setUp(self):
        """Desfine test variables and initialize app"""
        self.app = create_app("testing")
        self.client = self.app.test_client
        self.user = {'email': 'test_email@test_user', 'password': 'test_password'}

        # binds the app to the current context
        with self.app.app_context():
            db.create_all()

    def test_user_creation(self):
        """Test API can create a user (POST request) """
        response = self.client().post('/auth/register', data=self.user)
        self.assertEqual(response.status_code, 201)
        self.assertIn('test_email', str(response.data))

    def tearDown(self):
        """ teardown all initialized variables """
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
