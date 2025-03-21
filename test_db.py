# test_db.py

from app import create_app, db
from app.models import User  # Import the User model to test

# Create Flask app context
app = create_app()

# Test the database connection
with app.app_context():  # Use the Flask app context to run the code
    print("Testing database connection...")
    user = User.query.first()  # Query the first user, just to test if the DB is connected
    if user:
        print(f"User found: {user.username}")
    else:
        print("No users found in the database.")
