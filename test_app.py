import unittest
from app import app, db, User, Spending

class AppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up test environment (in-memory SQLite database)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        cls.client = app.test_client()

        # Initialize the database
        with app.app_context():
            db.create_all()

    def setUp(self):
        # Setup before each test
        pass

    def tearDown(self):
        # Cleanup after each test
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_user(self):
        # Test adding a user
        response = self.client.post('/add_user', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'age': 30
        })
        data = response.get_json()

        # Assert the user is added successfully
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'User added successfully')

        # Check if user exists in the database
        with app.app_context():
            user = User.query.filter_by(email='john@example.com').first()
            self.assertIsNotNone(user)

    def test_get_total_spending(self):
        # Test retrieving total spending for a user
        user = User(name='Jane Doe', email='jane@example.com', age=25)
        with app.app_context():
            db.session.add(user)
            db.session.commit()

        # Add some spending data
        spending = Spending(user_id=user.user_id, money_spent=100)
        with app.app_context():
            db.session.add(spending)
            db.session.commit()

        # Now test the total spending endpoint
        response = self.client.get(f'/total_spent/{user.user_id}')
        data = response.get_json()

        # Assert the total spending is returned correctly
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['total_spending'], 100)

if __name__ == '__main__':
    unittest.main()