import unittest
import json
from app import create_app, db, version

class BucketlistTestCase(unittest.TestCase):
    """This class represents the bucketlist test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.bucketlist = {'name': 'career goals'}

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
        return self.client().post(version + '/auth/register', data=user)

    def login_user(self, email='test@user.com', password='test_pass'):
        # methods helps login created user
        user = {
            'email': email,
            'password': password
        }
        return self.client().post(version + '/auth/login', data=user)

    def test_bucketlist_creation(self):
        """Test API can create a bucketlist (POST request)"""
        res = self.client().post(
            version + '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data=self.bucketlist
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn('career', str(res.data))

    def test_bucketlist_duplicate_name(self):
        """ handle duplicate names """
        # create bucketlist
        res = self.client().post(
            version + '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data=self.bucketlist
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn('career', str(res.data))

        # try to create one with same name
        res = self.client().post(
            version + '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data=self.bucketlist
        )
        self.assertEqual(res.status_code, 409)
        self.assertIn('Duplicate entry', str(res.data))

    def test_bucketlist_invalid_input(self):
        """ handle invalid user input """
        # no argument sent
        res = self.client().post(
            version + '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data={}
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn('Enter valid input', str(res.data))

        # user supplied space
        res = self.client().post(
            version + '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data={'name': ' '}
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn('Enter valid input', str(res.data))

        # user supplied empty string
        res = self.client().post(
            version + '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data={'name': ''}
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn('Enter valid input', str(res.data))

    def test_api_can_get_all_bucketlists(self):
        """Test API can get a bucketlist (GET request)."""
        res = self.client().post(
            version + '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data=self.bucketlist
        )
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            version + '/bucketlists/',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('career', str(res.data))

    def test_api_can_get_bucketlist_by_id(self):
        """Test API can get a single bucketlist by using it's id."""
        rv = self.client().post(
            version + '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data=self.bucketlist
        )
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            version + '/bucketlists/{}'.format(result_in_json['id']),
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(result.status_code, 200)
        self.assertIn('career', str(result.data))

    def test_bucketlist_can_be_edited(self):
        """Test API can edit an existing bucketlist. (PUT request)"""
        rv = self.client().post(
            version + '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data={'name': 'Lifestyle'}
        )
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            version + '/bucketlists/1',
            headers=dict(Authorization=self.access_token),
            data={
                "name": "Lifestyle goals"
            }
        )
        self.assertEqual(rv.status_code, 200)
        results = self.client().get(
            version + '/bucketlists/1',
            headers=dict(Authorization=self.access_token)
        )
        self.assertIn('goals', str(results.data))

        # update with duplicate name
        rv = self.client().put(
            version + '/bucketlists/1',
            headers=dict(Authorization=self.access_token),
            data={
                "name": "Lifestyle goals"
            }
        )
        self.assertEqual(rv.status_code, 409)
        self.assertIn('Duplicate entry', str(rv.data))

        """update with invalid input"""

        # no args
        rv = self.client().put(
            version + '/bucketlists/1',
            headers=dict(Authorization=self.access_token),
            data={}
        )
        self.assertEqual(rv.status_code, 400)
        self.assertIn('Enter valid input', str(rv.data))

        # user supplied space
        rv = self.client().put(
            version + '/bucketlists/1',
            headers=dict(Authorization=self.access_token),
            data={'name': ' '}
        )
        self.assertEqual(rv.status_code, 400)
        self.assertIn('Enter valid input', str(rv.data))

        # user supplied empty string
        rv = self.client().put(
            version + '/bucketlists/1',
            headers=dict(Authorization=self.access_token),
            data={'name': ''}
        )
        self.assertEqual(rv.status_code, 400)
        self.assertIn('Enter valid input', str(rv.data))

    def test_bucketlist_deletion(self):
        """Test API can delete an existing bucketlist. (DELETE request)."""
        rv = self.client().post(
            version + '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data={'name': 'Crazy goals'}
        )
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete(
            version + '/bucketlists/1',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get(
            version + '/bucketlists/1',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(result.status_code, 404)

    def test_bukcetlist_pagination(self):
        """ Testing bucketlist pagination """
        # we create some bucketlists first
        bucketlist_names = ['one', 'two', 'three', 'four', 'five', 'six']
        for i in bucketlist_names:
            response = self.client().post(
                version + '/bucketlists/',
                headers=dict(Authorization=self.access_token),
                data={'name': i}
            )
            self.assertEqual(response.status_code, 201)
            self.assertIn(i, str(response.data))
        # then test pagination
        # it should return five items for the first page
        response = self.client().get(
            version + '/bucketlists/?page=1&limit=5',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['number_of_bucketlists_on_page'], 5)
        self.assertIn('one', str(response.data))
        self.assertIn('two', str(response.data))
        self.assertIn('three', str(response.data))
        self.assertIn('four', str(response.data))
        self.assertIn('five', str(response.data))
        self.assertNotIn('six', str(response.data))
        # and one for the next page
        response = self.client().get(
            version + '/bucketlists/?page=2&limit=5',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['number_of_bucketlists_on_page'], 1)
        self.assertIn('six', str(response.data))
        self.assertNotIn('one', str(response.data))
        self.assertNotIn('two', str(response.data))
        self.assertNotIn('three', str(response.data))
        self.assertNotIn('four', str(response.data))
        self.assertNotIn('five', str(response.data))

        # test limit two
        # it should return two items for the first page
        response = self.client().get(
            version + '/bucketlists/?page=1&limit=2',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['number_of_bucketlists_on_page'], 2)
        self.assertIn('one', str(response.data))
        self.assertIn('two', str(response.data))
        self.assertNotIn('three', str(response.data))
        self.assertNotIn('four', str(response.data))
        self.assertNotIn('five', str(response.data))
        self.assertNotIn('six', str(response.data))
        # it should return two items for the second page
        response = self.client().get(
            version + '/bucketlists/?page=2&limit=2',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['number_of_bucketlists_on_page'], 2)
        self.assertIn('three', str(response.data))
        self.assertIn('four', str(response.data))
        self.assertNotIn('one', str(response.data))
        self.assertNotIn('two', str(response.data))
        self.assertNotIn('five', str(response.data))
        self.assertNotIn('six', str(response.data))
        # it should return two items for the third page
        response = self.client().get(
            version + '/bucketlists/?page=3&limit=2',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['number_of_bucketlists_on_page'], 2)
        self.assertIn('five', str(response.data))
        self.assertIn('six', str(response.data))
        self.assertNotIn('three', str(response.data))
        self.assertNotIn('four', str(response.data))
        self.assertNotIn('one', str(response.data))
        self.assertNotIn('two', str(response.data))

        # test limit zero
        # it should return no items for the all pages
        response = self.client().get(
            version + '/bucketlists/?page=1&limit=0',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['number_of_bucketlists_on_page'], 0)
        self.assertNotIn('one', str(response.data))
        self.assertNotIn('two', str(response.data))
        self.assertNotIn('three', str(response.data))
        self.assertNotIn('four', str(response.data))
        self.assertNotIn('five', str(response.data))
        self.assertNotIn('six', str(response.data))

        # test no limit
        # it should return all items for the first page
        response = self.client().get(
            version + '/bucketlists/?page=1',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(json.loads(response.data)['number_of_bucketlists_on_page'], 6)
        self.assertIn('one', str(response.data))
        self.assertIn('two', str(response.data))
        self.assertIn('three', str(response.data))
        self.assertIn('four', str(response.data))
        self.assertIn('five', str(response.data))
        self.assertIn('six', str(response.data))
        # should return none for the second page
        response = self.client().get(
            version + '/bucketlists/?page=2',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(json.loads(response.data)['number_of_bucketlists_on_page'], 0)
        self.assertNotIn('one', str(response.data))
        self.assertNotIn('two', str(response.data))
        self.assertNotIn('three', str(response.data))
        self.assertNotIn('four', str(response.data))
        self.assertNotIn('five', str(response.data))
        self.assertNotIn('six', str(response.data))

    def test_bucketlist_search(self):
        """ Test bucketlist search """
        # first add two test bucketlists
        bucketlist_names = ['search_one', 'search_two']
        for i in bucketlist_names:
            rv = self.client().post(
                version + '/bucketlists/',
                headers=dict(Authorization=self.access_token),
                data={'name': i}
            )
            self.assertEqual(rv.status_code, 201)
            self.assertIn(i, str(rv.data))
        # test search with query string: one
        rv = self.client().get(
            version + '/bucketlists/?q=one',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(rv.status_code, 200)
        self.assertIn('search_one', str(rv.data))
        self.assertNotIn('search_two', str(rv.data))
        # test search with query string: one - AnYcAsE
        rv = self.client().get(
            version + '/bucketlists/?q=OnE',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(rv.status_code, 200)
        self.assertIn('search_one', str(rv.data))
        # test search with query string: two
        rv = self.client().get(
            version + '/bucketlists/?q=two',
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(rv.status_code, 200)
        self.assertIn('search_two', str(rv.data))
        self.assertNotIn('search_one', str(rv.data))

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
