import unittest
import json
from app import app, db
from models import User, Spending

class FlaskAppTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up the Flask test client
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_users_vouchers.db'
        cls.client = app.test_client()

        # Create tables for testing
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        # Clean up after tests
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_user_valid(self):
        # Test adding a user with valid data
        response = self.client.post('/add_user', json={
            "name": "John Doe",
            "email": "john.doe@example.com",
            "age": 30
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("User added successfully", response.get_json().get("message"))

    def test_add_user_invalid(self):
        # Test adding a user with invalid data
        response = self.client.post('/add_user', json={
            "name": "",
            "age": 30
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_get_total_spending_valid_user(self):
        # Add a user and spending, then test total spending endpoint
        with app.app_context():
            user = User(name="Alice", email="alice@example.com", age=25)
            db.session.add(user)
            db.session.commit()

            spending = Spending(user_id=user.user_id, money_spent=150.00)
            db.session.add(spending)
            db.session.commit()

        response = self.client.get(f'/total_spent/{user.user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json().get("total_spending"), 150.00)

    def test_get_total_spending_invalid_user(self):
        # Test for a user that does not exist
        response = self.client.get('/total_spent/9999')
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.get_json())

    def test_average_spending_by_age(self):
        # Add users and spending, then test the average spending endpoint
        with app.app_context():
            user1 = User(name="Bob", email="bob@example.com", age=22)
            user2 = User(name="Charlie", email="charlie@example.com", age=29)
            db.session.add_all([user1, user2])
            db.session.commit()

            spending1 = Spending(user_id=user1.user_id, money_spent=100.00)
            spending2 = Spending(user_id=user2.user_id, money_spent=200.00)
            db.session.add_all([spending1, spending2])
            db.session.commit()

        response = self.client.get('/average_spending_by_age')
        self.assertEqual(response.status_code, 200)
        self.assertIn("average_spending_by_age", response.get_json())

    def test_write_to_mongodb_valid(self):
        # Test writing to MongoDB with valid data
        response = self.client.post('/write_to_mongodb', json={
            "user_id": 1,
            "total_spending": 500.00
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("Data successfully inserted", response.get_json().get("message"))

    def test_write_to_mongodb_invalid(self):
        # Test writing to MongoDB with invalid data
        response = self.client.post('/write_to_mongodb', json={
            "user_id": None,
            "total_spending": 500.00
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

if __name__ == '__main__':
    unittest.main()