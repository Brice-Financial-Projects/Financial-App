"""Test configuration and fixtures."""
import pytest
from app import create_app, db
from app.models import User, Profile, Budget
from flask_login import current_user

@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create a test user."""
    user = User(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_profile(app, test_user):
    """Create a test profile."""
    profile = Profile(
        user_id=test_user.id,
        first_name='Test',
        last_name='User',
        state='CA'
    )
    db.session.add(profile)
    db.session.commit()
    return profile

@pytest.fixture
def test_budget(app, test_user):
    """Create a test budget."""
    budget = Budget(
        name='Test Budget',
        user_id=test_user.id
    )
    db.session.add(budget)
    db.session.commit()
    return budget

@pytest.fixture
def auth_client(client, test_user):
    """Create an authenticated test client."""
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
    return client 