import unittest
import json
from app import create_app, db

class BucketlistTestCase(unittest.TestCase):
    """This class represents the bucketlist test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.bucketlist = {'name': 'Career goals'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
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

    def test_bucketlist_creation(self):
        """Test API can create a bucketlist (POST request)"""
        res = self.client().post(
            '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data=self.bucketlist
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn('Career', str(res.data))

    def test_api_can_get_all_bucketlists(self):
        """Test API can get a bucketlist (GET request)."""
        res = self.client().post(
            '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data=self.bucketlist
        )
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            '/bucketlists/',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Career', str(res.data))

    def test_api_can_get_bucketlist_by_id(self):
        """Test API can get a single bucketlist by using it's id."""
        rv = self.client().post(
            '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data=self.bucketlist
        )
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/bucketlists/{}'.format(result_in_json['id']),
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(result.status_code, 200)
        self.assertIn('Career', str(result.data))

    def test_bucketlist_can_be_edited(self):
        """Test API can edit an existing bucketlist. (PUT request)"""
        rv = self.client().post(
            '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data={'name': 'Lifestyle'}
        )
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            '/bucketlists/1',
            headers=dict(Authorization=self.access_token),
            data={
                "name": "Lifestyle goals"
            }
        )
        self.assertEqual(rv.status_code, 200)
        results = self.client().get(
            '/bucketlists/1',
            headers=dict(Authorization=self.access_token)
        )
        self.assertIn('goals', str(results.data))

    def test_bucketlist_deletion(self):
        """Test API can delete an existing bucketlist. (DELETE request)."""
        rv = self.client().post(
            '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data={'name': 'Crazy goals'}
        )
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete(
            '/bucketlists/1',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get(
            '/bucketlists/1',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(result.status_code, 404)

    """ Testing pagination """
    def test_bukcetlist_pagination(self):
        # we create some bucketlists first
        bucketlist_names = ['one', 'two', 'three', 'four', 'five', 'six']
        for i in bucketlist_names:
            response = self.client().post(
                '/bucketlists/',
                headers=dict(Authorization=self.access_token),
                data={'name': i}
            )
            self.assertEqual(response.status_code, 201)
            self.assertIn(i, str(response.data))

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
