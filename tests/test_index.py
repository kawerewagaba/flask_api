import unittest
import json
from app import create_app, version

class ItemTestCase(unittest.TestCase):
    """ test if landing page loads """

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client

    # test index endpoint
    def test_index(self):
        response = self.client().get(
            '/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Bucketlist Flask API', str(response.data))

    # test version endpoint
    def test_version(self):
        response = self.client().get(
            version
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Bucketlist Flask API', str(response.data))

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
