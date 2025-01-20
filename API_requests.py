import requests

# Base URL for the Flask app
BASE_URL = "http://127.0.0.1:5000"  # Adjust the port if necessary

def fetch_total_spending():
    """
    Retrieve the total spending for all users in the database.
    """
    try:
        endpoint = f"{BASE_URL}/total_spent_all_users"
        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
            print("\nTotal Spending for All Users:")
            for user in data["total_spendings"]:
                print(f"User ID: {user['user_id']}, Total Spending: {user['total_spending']}")
        else:
            print(f"Failed to retrieve total spending. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while fetching total spending: {str(e)}")

def write_eligible_users():
    """
    Write eligible users (spending > 1000) to the MongoDB database.
    """
    try:
        endpoint = f"{BASE_URL}/write_eligible_users_to_mongodb"
        response = requests.post(endpoint)
        if response.status_code == 201:
            print("\nEligible users' data successfully written to MongoDB.")
        elif response.status_code == 404:
            print("\nNo eligible users found.")
        else:
            print(f"Failed to write eligible users. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while writing eligible users: {str(e)}")

def fetch_average_spending_by_age():
    """
    Fetch the average spending grouped by age ranges.
    """
    try:
        endpoint = f"{BASE_URL}/average_spending_by_age"
        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
            print("\nAverage Spending by Age Ranges:")
            # Extract the average spending by age ranges from the response
            averages = data.get("average_spending_by_age", {})
            for age_range, avg_spending in averages.items():
                print(f"Age Range: {age_range}, Average Spending: {avg_spending:.2f}")
        else:
            print(f"Failed to retrieve average spending by age. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while fetching average spending by age: {str(e)}")

# Execute API requests
if __name__ == "__main__":
    fetch_total_spending()  # Step 1: Retrieve total spending for all users
    write_eligible_users()  # Step 2: Write eligible users to MongoDB
    fetch_average_spending_by_age()  # Step 3: Fetch average spending by age ranges