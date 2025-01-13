from flask import Flask, request, jsonify
from extensions import db
from models import User, Spending
from pymongo import MongoClient

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_vouchers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# MongoDB configuration
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["spending_db"]
mongo_collection = mongo_db["high_spending_users"]

# Initialize the database with the app
db.init_app(app)

# Create tables at startup
with app.app_context():
    db.create_all()

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

    # (Optional) Send results to Telegram using a bot (requires additional setup)
    # send_to_telegram(averages)

    return jsonify({"average_spending_by_age": averages}), 200

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
    app.run(debug=True)