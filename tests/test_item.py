import unittest
import json
from app import create_app, db

class ItemTestCase(unittest.TestCase):
    """This class represents the item test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.item = {'name': 'buy a tesla'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

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

    def create_bucketlist(self, name='Lifestyle'):
        # method helps to create a bucketlist
        # register a test user then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it.
        bucketlist = {
            'name': name
        }
        return self.client().post(
            '/bucketlists/',
            headers=dict(Authorization='Bearer ' + access_token),
            data=bucketlist
        )

    def test_add_item(self):
        """ test API can add items to bucketlist """
        result = self.create_bucketlist()
        # we need to obtain bucketlist ID
        bucketlist_id = json.loads(result.data.decode())['id']
        res = self.client().post(
            '/bucketlists/{}/items/'.format(bucketlist_id),
            data=self.item
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn('tesla', str(res.data))
