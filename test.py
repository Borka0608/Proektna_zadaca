from flask import Flask
from extensions import db
from models import User

# Initialize the Flask app (use the same configuration as in your app)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_vouchers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)


# Test function to query and display users
def test_read_users():
    # Open the Flask app context to interact with the database
    with app.app_context():
        # Query all users in the database
        users = User.query.all()

        if not users:
            print("No users found in the database.")
        else:
            print("Users found in the database:")
            for user in users:
                print(f"User ID: {user.user_id}, Age: {user.age}")


# Call the test function
if __name__ == '__main__':
    test_read_users()