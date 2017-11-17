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

    def test_user_duplicate_email(self):
        """ handle duplicate user """
        # register a user with details that exist
        response = self.client().post(
            '/auth/register',
            data={'email': 'test@user.com', 'password': 'test_pass'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('already taken', str(response.data))

    def test_user_invalid_input(self):
        """ handle invalid input """
        # no email
        response = self.client().post(
            '/auth/register',
            data={'email': '', 'password': 'test_pass'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Enter valid input', str(response.data))

        # email is space
        response = self.client().post(
            '/auth/register',
            data={'email': ' ', 'password': 'test_pass'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Enter valid input', str(response.data))

        # no password
        response = self.client().post(
            '/auth/register',
            data={'email': 'invalid@user.com', 'password': ''}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Enter valid input', str(response.data))

        # password is space
        response = self.client().post(
            '/auth/register',
            data={'email': 'invalid@user.com', 'password': ' '}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Enter valid input', str(response.data))

        # no email and password
        response = self.client().post(
            '/auth/register',
            data={'email': '', 'password': ''}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Enter valid input', str(response.data))

        # no keys sent
        response = self.client().post(
            '/auth/register',
            data={}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Enter valid input', str(response.data))

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

        # no keys sent
        response = self.client().post(
            '/auth/login',
            data={}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Enter valid input', str(response.data))

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
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(response.status_code, 401)
        # try to edit bucketlist
        response = self.client().put(
            '/bucketlists/1',
            headers=dict(Authorization=self.access_token),
            data={"name": "Lifestyle goals"}
        )
        self.assertEqual(response.status_code, 401)
        # try to view items in bucketlist
        response = self.client().get(
            '/bucketlists/1/items/',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(response.status_code, 401)
        # try to edit item in bucketlist
        response = self.client().put(
            '/bucketlists/1/items/1',
            headers=dict(Authorization=self.access_token),
            data={'name': 'build a family house'}
        )
        self.assertEqual(response.status_code, 401)

    def test_user_reset_password(self):
        """Test API allows password reset"""
        response = self.client().post(
            '/auth/reset-password',
            data={
                'access_token': self.access_token,
                'password': 'new_pass'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('reset', str(response.data))
        # try login with previous password. it should fail
        login_response = self.client().post('/auth/login', data=self.user)
        self.assertIn('Verify credentials and try again', str(login_response.data))
        self.assertEqual(login_response.status_code, 401)
        # try login with new password. it should pass
        login_response = self.client().post('/auth/login',
            data={
                'email': 'test@user.com',
                'password': 'new_pass'
            }
        )
        self.assertIn('You logged in successfully', str(login_response.data))
        self.assertEqual(login_response.status_code, 200)

        """ test resource access after password reset. It shoud fail. """
        # try to view bucketlists
        response = self.client().get(
            '/bucketlists/',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(response.status_code, 401)

    def tearDown(self):
        """ teardown all initialized variables """
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
