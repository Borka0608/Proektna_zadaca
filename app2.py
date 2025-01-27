from flask import Flask, request, jsonify
from extensions import db
from models import User, Spending
from pymongo import MongoClient
import requests  # To make HTTP requests to Telegram API

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_vouchers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# MongoDB Configuration (updated for MongoDB Atlas)
mongo_client = MongoClient("mongodb+srv://bmicovska:A0lWi5qm7IRGjRfQ@cluster3.lbxxg.mongodb.net/Borka_proekt?retryWrites=true&w=majority")
mongo_db = mongo_client["Borka_proekt"]  # Use the "Borka_proekt" database
mongo_collection = mongo_db["high_spending_users"]  # Use the "high_spending_users" collection

# Initialize the database with the app
db.init_app(app)

# Create tables at startup
with app.app_context():
    db.create_all()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = '8103611758:AAHjD5oKMZ_8NVLQhuVeaWSuAvH4GPtMPYI'  # your_telegram_bot_token_here
TELEGRAM_CHAT_ID = '7443955787'


def send_to_telegram(message):
    """
    Sends a message to a specific Telegram chat.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, json=payload)
    return response.json()


# Endpoint: Add New User
@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        age = data.get("age")

        if not name or age is None:
            return jsonify({"error": "Name and age are required"}), 400

        new_user = User(name=name, email=email, age=age)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User added successfully", "user_id": new_user.user_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint: Retrieve Total Spending for All Users
@app.route('/total_spent_all_users', methods=['GET'])
def total_spent_all_users():
    try:
        results = db.session.query(User.user_id, db.func.sum(Spending.money_spent).label('total_spending')) \
            .join(Spending, Spending.user_id == User.user_id) \
            .group_by(User.user_id).all()

        total_spendings = [{"user_id": result.user_id, "total_spending": result.total_spending} for result in results]
        return jsonify({"total_spendings": total_spendings}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint: Retrieve Total Spending for Eligible Users
@app.route('/eligible_users', methods=['GET'])
def eligible_users():
    try:
        results = db.session.query(User.user_id, db.func.sum(Spending.money_spent).label('total_spending')) \
            .join(Spending, Spending.user_id == User.user_id) \
            .group_by(User.user_id).all()

        eligible_users = [{"user_id": result.user_id, "total_spending": result.total_spending}
                          for result in results if result.total_spending > 1000]
        return jsonify({"eligible_users": eligible_users}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint: Write Eligible Users to MongoDB (Cloud)
@app.route('/write_eligible_users_to_mongodb', methods=['POST'])
def write_eligible_users_to_mongodb():
    try:
        # Fetch eligible users from the /eligible_users route
        print("Received request to write eligible users to MongoDB.")
        response = requests.get("http://127.0.0.1:5000/eligible_users")

        if response.status_code == 200:
            eligible_users = response.json().get("eligible_users", [])
            print(f"Fetched eligible users: {eligible_users}")

            if not eligible_users:
                return jsonify({"message": "No eligible users found"}), 404

            # Debugging the data being passed to MongoDB
            print(f"Eligible users to insert into MongoDB: {eligible_users}")

            # Attempt to insert data into MongoDB
            result = mongo_collection.insert_many(eligible_users)

            # After insertion, let's check and log the result
            print(f"Inserted IDs: {result.inserted_ids}")

            # Check if no IDs are inserted
            if not result.inserted_ids:
                print("No documents inserted into MongoDB!")
                return jsonify({"error": "Failed to insert documents into MongoDB"}), 500

            # Return successful response
            return jsonify({"message": "Eligible users' data successfully written to MongoDB Cloud"}), 201
        else:
            print(f"Failed to fetch eligible users, status code: {response.status_code}")
            return jsonify({"error": "Failed to fetch eligible users"}), 500
    except Exception as e:
        print(f"Error inserting data: {str(e)}")  # Log any exception
        return jsonify({"error": str(e)}), 500


# Endpoint: Retrieve Total Spending by User
@app.route('/total_spent/<int:user_id>', methods=['GET'])
def get_total_spending(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    total_spending = db.session.query(db.func.sum(Spending.money_spent)).filter_by(user_id=user_id).scalar()
    return jsonify({"user_id": user_id, "total_spending": total_spending or 0}), 200


# Endpoint: Calculate Average Spending by Age Ranges
@app.route('/average_spending_by_age', methods=['GET'])
def average_spending_by_age():
    age_ranges = {
        "18-24": (18, 24),
        "25-30": (25, 30),
        "31-36": (31, 36),
        "37-47": (37, 47),
        ">47": (48, 150)
    }

    averages = {}
    for age_range, (min_age, max_age) in age_ranges.items():
        avg_spending = (
            db.session.query(db.func.avg(Spending.money_spent))
            .join(User)
            .filter(User.age.between(min_age, max_age))
            .scalar()
        )
        averages[age_range] = avg_spending or 0

    message = "📊 Average Spending by Age Range:\n"
    for age_range, avg_spending in averages.items():
        message += f"- {age_range}: ${avg_spending:.2f}\n"

    telegram_response = send_to_telegram(message)
    return jsonify({
        "average_spending_by_age": averages,
        "telegram_status": telegram_response
    }), 200


# Endpoint: Write User Data to MongoDB
@app.route('/write_to_mongodb', methods=['POST'])
def write_to_mongodb():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        total_spending = data.get("total_spending")

        if not user_id or not total_spending:
            return jsonify({"error": "Invalid data"}), 400

        mongo_document = {"user_id": user_id, "total_spending": total_spending}
        mongo_collection.insert_one(mongo_document)

        return jsonify({"message": "Data successfully inserted into MongoDB"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Test MongoDB connection
    try:
        mongo_client.admin.command('ping')
        print("Successfully connected to MongoDB Atlas")
    except Exception as e:
        print(f"MongoDB connection failed: {str(e)}")

    app.run(debug=True)
