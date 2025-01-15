from extensions import db

# Define the User model
class User(db.Model):
    __tablename__ = 'user_info'

    user_id = db.Column(db.Integer, primary_key=True)  # Primary Key
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    age = db.Column(db.Integer, nullable=True)

    # Relationship to Spending model
    spendings = db.relationship('Spending', backref='user', lazy=True)

    def __repr__(self):
        return f"<User user_id={self.user_id} name={self.name} age={self.age}>"

# Define the Spending model
class Spending(db.Model):
    __tablename__ = 'user_spending'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Implicit Primary Key
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.user_id'), nullable=False)
    money_spent = db.Column(db.Float, nullable=False, default=0.0)  # Renamed to 'amount' to match endpoint
    year = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Spending user_id={self.user_id} amount={self.amount} year={self.year}>"