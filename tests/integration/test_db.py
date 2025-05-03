"""Integration tests for database operations."""
import pytest
from app import db
from app.models import User, Profile, Budget, BudgetItem, ExpenseCategory
from datetime import date

def test_user_profile_relationship(test_db):
    """
    GIVEN a User model and Profile model
    WHEN a new User and Profile are created with a relationship
    THEN check the relationship works correctly
    """
    # Create and save a user
    user = User(username='testuser', email='test@test.com', password='password123')
    db.session.add(user)
    db.session.commit()

    # Create and save a profile linked to the user
    profile = Profile(
        user_id=user.id,
        first_name='John',
        last_name='Doe',
        state='CA',
        filing_status='single',
        income_type='Salary',
        pay_cycle='biweekly',
        retirement_contribution_type='pretax'
    )
    db.session.add(profile)
    db.session.commit()

    # Test relationships
    assert user.profile == profile
    assert profile.user == user

def test_budget_cascade_delete(test_db):
    """
    GIVEN a User with a Profile and Budget
    WHEN the User is deleted
    THEN check that related Profile and Budgets are also deleted
    """
    # Create user and profile
    user = User(username='budgetuser', email='budget@test.com', password='password123')
    db.session.add(user)
    db.session.commit()

    profile = Profile(
        user_id=user.id,
        first_name='John',
        last_name='Doe',
        state='CA',
        filing_status='single',
        income_type='Salary',
        pay_cycle='biweekly',
        retirement_contribution_type='pretax'
    )
    db.session.add(profile)
    db.session.commit()

    # Create budget
    budget = Budget(
        user_id=user.id,
        profile_id=profile.id,
        name='Test Budget',
        gross_income=50000
    )
    db.session.add(budget)
    db.session.commit()

    # Delete user and verify cascade
    db.session.delete(user)
    db.session.commit()

    # Verify everything is deleted
    assert User.query.filter_by(id=user.id).first() is None
    assert Profile.query.filter_by(id=profile.id).first() is None
    assert Budget.query.filter_by(id=budget.id).first() is None

def test_budget_items_relationship(test_db):
    """
    GIVEN a Budget with multiple BudgetItems
    WHEN items are added and queried
    THEN check the relationships work correctly
    """
    # Create necessary parent objects
    user = User(username='itemuser', email='items@test.com', password='password123')
    db.session.add(user)
    db.session.commit()

    profile = Profile(
        user_id=user.id,
        first_name='John',
        last_name='Doe',
        state='CA',
        filing_status='single',
        income_type='Salary',
        pay_cycle='biweekly',
        retirement_contribution_type='pretax'
    )
    db.session.add(profile)
    db.session.commit()

    # Create budget
    budget = Budget(
        user_id=user.id,
        profile_id=profile.id,
        name='Item Test Budget',
        gross_income=50000
    )
    db.session.add(budget)
    db.session.commit()

    # Create budget items
    items = [
        BudgetItem(
            budget_id=budget.id,
            category='Housing',
            name='Rent',
            minimum_payment=1000,
            preferred_payment=1200
        ),
        BudgetItem(
            budget_id=budget.id,
            category='Utilities',
            name='Electricity',
            minimum_payment=50,
            preferred_payment=75
        )
    ]
    db.session.bulk_save_objects(items)
    db.session.commit()

    # Verify relationships
    budget_from_db = Budget.query.get(budget.id)
    assert len(budget_from_db.budget_items) == 2
    assert any(item.name == 'Rent' for item in budget_from_db.budget_items)
    assert any(item.name == 'Electricity' for item in budget_from_db.budget_items)

def test_unique_constraints(test_db):
    """
    GIVEN database constraints
    WHEN duplicate data is inserted
    THEN check that appropriate errors are raised
    """
    # Create initial user
    user1 = User(username='uniqueuser', email='unique@test.com', password='password123')
    db.session.add(user1)
    db.session.commit()

    # Try to create user with same username
    with pytest.raises(Exception):  # Should be more specific based on your DB
        user2 = User(username='uniqueuser', email='different@test.com', password='password123')
        db.session.add(user2)
        db.session.commit()

    # Try to create user with same email
    with pytest.raises(Exception):  # Should be more specific based on your DB
        user3 = User(username='differentuser', email='unique@test.com', password='password123')
        db.session.add(user3)
        db.session.commit() 