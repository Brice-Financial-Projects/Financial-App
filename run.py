"""run.py"""

from app import create_app

# Create the app instance using the factory function
app = create_app()

if __name__ == '__main__':
    # Run the app
    app.run(port=5000)
