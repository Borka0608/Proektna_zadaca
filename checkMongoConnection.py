from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017/")
    print("MongoDB connection successful!")
    db = client["spending_db"]
    print("Databases:", client.list_database_names())
except Exception as e:
    print("MongoDB connection failed:", e)