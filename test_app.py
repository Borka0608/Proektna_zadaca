import unittest
from unittest.mock import MagicMock
import json
from app import app, db, mongo_client  # Assuming you have mongo_client imported
from models import User, Spending

class AppTestCase(unittest.TestCase):
    def setUp(self):
        """
        Setup the Flask test client and initialize the database with in-memory SQLite.
        """
        self.app = app.test_client()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory SQLite
        app.config['TESTING'] = True

        # Mock the MongoDB client
        self.mongo_mock = MagicMock()
        self.mongo_client = self.mongo_mock  # Replace real mongo_client with mock

        # Ensure the database tables exist
        with app.app_context():
            db.create_all()

    def test_add_user(self):
        """
        Test the /add_user endpoint.
        """
        payload = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "age": 30
        }
        response = self.app.post('/add_user', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn("User added successfully", response.json["message"])

    def test_total_spent_all_users(self):
        """
        Test the /total_spent_all_users endpoint.
        """
        response = self.app.get('/total_spent_all_users')
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_spendings", response.json)

    def test_eligible_users(self):
        """
        Test the /eligible_users endpoint.
        """
        response = self.app.get('/eligible_users')
        self.assertEqual(response.status_code, 200)
        self.assertIn("eligible_users", response.json)

    def test_get_total_spending(self):
        """
        Test the /total_spent/<int:user_id> endpoint.
        """
        user_id = 1  # Ensure a valid user ID exists in the database
        response = self.app.get(f'/total_spent/{user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_spending", response.json)

    def test_average_spending_by_age(self):
        """
        Test the /average_spending_by_age endpoint.
        """
        response = self.app.get('/average_spending_by_age')
        self.assertEqual(response.status_code, 200)
        self.assertIn("average_spending_by_age", response.json)

    def tearDown(self):
        """
        Cleanup operations after each test.
        """
        with app.app_context():
            db.session.remove()
            db.engine.dispose()  # Close the SQLAlchemy engine connection

        # Reset the MongoDB mock between tests
        self.mongo_mock.reset_mock()

if __name__ == '__main__':
    unittest.main()  # This will ensure that all the tests are discovered and run