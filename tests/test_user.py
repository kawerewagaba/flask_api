"""Tests user resgidtration, and authentication"""

import unittest
import json

from app import create_app, db, revoked_tokens

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

            # register a test user then log them in
            self.register_user()
            result = self.login_user()
            # obtain the access token
            self.access_token = json.loads(result.data.decode())['access_token']

    def register_user(self, email='test@user.com', password='test_pass'):
        # method helps us create a new user
        user = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/register', data=user)

    def login_user(self, email='test@user.com', password='test_pass'):
        # methods helps login created user
        user = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/login', data=user)

    def test_user_creation(self):
        """Test API can create a user (POST request) """
        response = self.client().post('/auth/register', data=self.user)
        self.assertEqual(response.status_code, 201)
        self.assertIn(self.user['email'], str(response.data))

    def test_user_login(self):
        """Test API can login user"""
        # first create a user in the test_db
        response = self.client().post('/auth/register', data=self.user)
        self.assertEqual(response.status_code, 201)
        # then try to login
        login_response = self.client().post('/auth/login', data=self.user)
        #first make sure data is passed back
        self.assertEqual(login_response.status_code, 200)
        #get the results in json format
        result = json.loads(login_response.data)
        self.assertEqual(result['message'], "You logged in successfully")
        # test that there is an access token created
        self.assertTrue(result['access_token'])

    def test_user_logout(self):
        """Test API can logout user"""
        # request to logout
        response = self.client().post('/auth/logout', data={'access_token': self.access_token})
        self.assertEqual(json.loads(response.data)['message'], 'You logged out successfully')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.access_token, str(revoked_tokens))
        # try to view bucketlists
        response = self.client().get(
            '/bucketlists/',
            headers=dict(Authorization='Bearer ' + self.access_token)
        )
        self.assertEqual(response.status_code, 401)

    def test_user_reset_password(self):
        """Test API allows password reset"""
        pass

    def tearDown(self):
        """ teardown all initialized variables """
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
