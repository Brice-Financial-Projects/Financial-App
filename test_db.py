# test_db.py
import os
from app import create_app, db
from app.models import User  # Import the User model to test

# Print environment variables
print(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

# Create Flask app context
app = create_app()

# Print actual database connection string from app config
print(f"SQLALCHEMY_DATABASE_URI from app config: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Test the database connection
with app.app_context():  # Use the Flask app context to run the code
    print("Testing database connection...")
    user = User.query.first()  # Query the first user, just to test if the DB is connected
    if user:
        print(f"User found: {user.username}")
    else:
        print("No users found in the database.")
