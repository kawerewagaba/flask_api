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

    def create_bucketlist(self, name='Lifestyle'):
        # method helps to create a bucketlist
        bucketlist = {
            'name': name
        }
        return self.client().post(
            '/bucketlists/',
            headers=dict(Authorization=self.access_token),
            data=bucketlist
        )

    def test_add_item(self):
        """ test API can add items to bucketlist """
        result = self.create_bucketlist()
        # we need to obtain bucketlist ID
        bucketlist_id = json.loads(result.data.decode())['id']
        res = self.client().post(
            '/bucketlists/{}/items/'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token),
            data=self.item
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn('tesla', str(res.data))

    def test_item_duplicate_name(self):
        """ test duplicate item names """
        result = self.create_bucketlist()
        # we need to obtain bucketlist ID
        bucketlist_id = json.loads(result.data.decode())['id']
        res = self.client().post(
            '/bucketlists/{}/items/'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token),
            data=self.item
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn('tesla', str(res.data))

        # try adding one with the same name
        res = self.client().post(
            '/bucketlists/{}/items/'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token),
            data=self.item
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Duplicate entry', str(res.data))

    def test_item_invalid_input(self):
        """ test invalid user input """
        # no arguments sent
        result = self.create_bucketlist()
        # we need to obtain bucketlist ID
        bucketlist_id = json.loads(result.data.decode())['id']
        res = self.client().post(
            '/bucketlists/{}/items/'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token),
            data={}
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Enter valid input', str(res.data))

        # user supplied space
        res = self.client().post(
            '/bucketlists/{}/items/'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token),
            data={'name': ' '}
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Enter valid input', str(res.data))

        # user supplied empty string
        res = self.client().post(
            '/bucketlists/{}/items/'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token),
            data={'name': ''}
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Enter valid input', str(res.data))

    def test_get_items_in_bucketlist(self):
        """ test API gets items in a bucketlist """
        result = self.create_bucketlist()
        # we need to obtain bucketlist ID
        bucketlist_id = json.loads(result.data.decode())['id']
        # first add the item
        res = self.client().post(
            '/bucketlists/{}/items/'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token),
            data=self.item
        )
        # then check if it exists
        res = self.client().get(
            '/bucketlists/{}/items/'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('tesla', str(res.data))

    def test_edit_item_in_bucketlist(self):
        """ test API can edit item in bucketlist """
        result = self.create_bucketlist()
        # we need to obtain bucketlist ID
        bucketlist_id = json.loads(result.data.decode())['id']
        # first add the item
        res = self.client().post(
            '/bucketlists/{}/items/'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token),
            data=self.item
        )
        # edit item
        item_id = json.loads(res.data.decode())['id']
        res = self.client().put(
            '/bucketlists/{}/items/{}'.format(bucketlist_id, item_id),
            headers=dict(Authorization=self.access_token),
            data={'name': 'build a family house'}
        )
        self.assertEqual(res.status_code, 201)
        # then check if it has changed
        res = self.client().get(
            '/bucketlists/{}/items/{}'.format(bucketlist_id, item_id),
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('house', str(res.data))

        # update with duplicate name
        res = self.client().put(
            '/bucketlists/{}/items/{}'.format(bucketlist_id, item_id),
            headers=dict(Authorization=self.access_token),
            data={'name': 'build a family house'}
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Duplicate entry', str(res.data))

        """update with invalid input"""

        # no args
        res = self.client().put(
            '/bucketlists/{}/items/{}'.format(bucketlist_id, item_id),
            headers=dict(Authorization=self.access_token),
            data={}
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Enter valid input', str(res.data))

        # user supplied space
        res = self.client().put(
            '/bucketlists/{}/items/{}'.format(bucketlist_id, item_id),
            headers=dict(Authorization=self.access_token),
            data={'name': ' '}
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Enter valid input', str(res.data))

        # user supplied empty string
        res = self.client().put(
            '/bucketlists/{}/items/{}'.format(bucketlist_id, item_id),
            headers=dict(Authorization=self.access_token),
            data={'name': ''}
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Enter valid input', str(res.data))

    def test_bukcetlist_item_pagination(self):
        """ Testing item pagination """
        result = self.create_bucketlist()
        # we need to obtain bucketlist ID
        bucketlist_id = json.loads(result.data.decode())['id']
        # we create some items first
        item_names = ['one', 'two', 'three', 'four', 'five', 'six']
        for i in item_names:
            response = self.client().post(
                '/bucketlists/{}/items/'.format(bucketlist_id),
                headers=dict(Authorization=self.access_token),
                data={'name': i}
            )
            self.assertEqual(response.status_code, 201)
            self.assertIn(i, str(response.data))
        # then test pagination
        # it should return five items for the first page
        response = self.client().get(
            '/bucketlists/{}/items/?page=1&limit=5'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['number_of_bucketlist_items_on_page'], 5)
        self.assertIn('one', str(response.data))
        self.assertIn('two', str(response.data))
        self.assertIn('three', str(response.data))
        self.assertIn('four', str(response.data))
        self.assertIn('five', str(response.data))
        self.assertNotIn('six', str(response.data))
        # and one for the next page
        response = self.client().get(
            '/bucketlists/{}/items/?page=2&limit=5'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['number_of_bucketlist_items_on_page'], 1)
        self.assertIn('six', str(response.data))
        self.assertNotIn('one', str(response.data))
        self.assertNotIn('two', str(response.data))
        self.assertNotIn('three', str(response.data))
        self.assertNotIn('four', str(response.data))
        self.assertNotIn('five', str(response.data))

        # test limit two
        # it should return two items for the first page
        response = self.client().get(
            '/bucketlists/{}/items/?page=1&limit=2'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['number_of_bucketlist_items_on_page'], 2)
        self.assertIn('one', str(response.data))
        self.assertIn('two', str(response.data))
        self.assertNotIn('three', str(response.data))
        self.assertNotIn('four', str(response.data))
        self.assertNotIn('five', str(response.data))
        self.assertNotIn('six', str(response.data))
        # it should return two items for the second page
        response = self.client().get(
            '/bucketlists/{}/items/?page=2&limit=2'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['number_of_bucketlist_items_on_page'], 2)
        self.assertIn('three', str(response.data))
        self.assertIn('four', str(response.data))
        self.assertNotIn('one', str(response.data))
        self.assertNotIn('two', str(response.data))
        self.assertNotIn('five', str(response.data))
        self.assertNotIn('six', str(response.data))
        # it should return two items for the third page
        response = self.client().get(
            '/bucketlists/{}/items/?page=3&limit=2'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['number_of_bucketlist_items_on_page'], 2)
        self.assertIn('five', str(response.data))
        self.assertIn('six', str(response.data))
        self.assertNotIn('three', str(response.data))
        self.assertNotIn('four', str(response.data))
        self.assertNotIn('one', str(response.data))
        self.assertNotIn('two', str(response.data))

        # test limit zero
        # it should return no items for the all pages
        response = self.client().get(
            '/bucketlists/{}/items/?page=1&limit=0'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['number_of_bucketlist_items_on_page'], 0)
        self.assertNotIn('one', str(response.data))
        self.assertNotIn('two', str(response.data))
        self.assertNotIn('three', str(response.data))
        self.assertNotIn('four', str(response.data))
        self.assertNotIn('five', str(response.data))
        self.assertNotIn('six', str(response.data))

        # test no limit
        # it should return all items for the first page
        response = self.client().get(
            '/bucketlists/{}/items/?page=1'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(json.loads(response.data)['number_of_bucketlist_items_on_page'], 6)
        self.assertIn('one', str(response.data))
        self.assertIn('two', str(response.data))
        self.assertIn('three', str(response.data))
        self.assertIn('four', str(response.data))
        self.assertIn('five', str(response.data))
        self.assertIn('six', str(response.data))
        # should return none for the second page
        response = self.client().get(
            '/bucketlists/{}/items/?page=2'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(json.loads(response.data)['number_of_bucketlist_items_on_page'], 0)
        self.assertNotIn('one', str(response.data))
        self.assertNotIn('two', str(response.data))
        self.assertNotIn('three', str(response.data))
        self.assertNotIn('four', str(response.data))
        self.assertNotIn('five', str(response.data))
        self.assertNotIn('six', str(response.data))

    def test_bukcetlist_item_search(self):
        """ Testing item search """
        result = self.create_bucketlist()
        # we need to obtain bucketlist ID
        bucketlist_id = json.loads(result.data.decode())['id']
        # first add two test items
        item_names = ['search_one', 'search_two']
        for i in item_names:
            rv = self.client().post(
                '/bucketlists/{}/items/'.format(bucketlist_id),
                headers=dict(Authorization=self.access_token),
                data={'name': i}
            )
            self.assertEqual(rv.status_code, 201)
            self.assertIn(i, str(rv.data))
        # test search with query string: one
        rv = self.client().get(
            '/bucketlists/{}/items/?q=one'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(rv.status_code, 200)
        self.assertIn('search_one', str(rv.data))
        self.assertNotIn('search_two', str(rv.data))
        # test search with query string: one - AnYcAsE
        rv = self.client().get(
            '/bucketlists/{}/items/?q=OnE'.format(bucketlist_id),
            headers=dict(Authorization=self.access_token)
        )
        self.assertEqual(rv.status_code, 200)
        self.assertIn('search_one', str(rv.data))
        # test search with query string: two
        rv = self.client().get(
            '/bucketlists/{}/items/?q=two'.format(bucketlist_id),
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
