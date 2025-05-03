"""Unit tests for database models."""
import pytest
from datetime import datetime, date
from app.models import User, Profile, Budget, ExpenseCategory, BudgetItem

def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, password hash, and other fields are defined correctly
    """
    user = User('testuser', 'test@test.com', 'password123')
    assert user.username == 'testuser'
    assert user.email == 'test@test.com'
    assert user.password_hash != 'password123'
    assert user.check_password('password123')
    assert not user.check_password('wrongpassword')
    assert user.is_authenticated
    assert user.is_active
    assert not user.is_anonymous
    assert not user.is_admin

def test_profile_creation():
    """
    GIVEN a Profile model
    WHEN a new Profile is created
    THEN check all fields are set correctly
    """
    profile = Profile(
        user_id=1,
        first_name='John',
        last_name='Doe',
        state='CA',
        filing_status='single',
        income_type='Salary',
        pay_cycle='biweekly',
        retirement_contribution_type='pretax'
    )
    assert profile.first_name == 'John'
    assert profile.last_name == 'Doe'
    assert profile.state == 'CA'
    assert profile.filing_status == 'single'
    assert profile.num_dependents == 0
    assert profile.income_type == 'Salary'
    assert profile.pay_cycle == 'biweekly'

def test_profile_total_pretax_deductions():
    """
    GIVEN a Profile with various pre-tax deductions
    WHEN total_pretax_deductions is calculated
    THEN check the calculation is correct
    """
    profile = Profile(
        user_id=1,
        first_name='John',
        last_name='Doe',
        state='CA',
        filing_status='single',
        income_type='Salary',
        pay_cycle='biweekly',
        retirement_contribution_type='pretax',
        retirement_contribution=5000,
        health_insurance_premium=2000,
        hsa_contribution=1000,
        fsa_contribution=500,
        other_pretax_benefits=1000
    )
    assert profile.total_pretax_deductions == 9500

def test_profile_age_calculation():
    """
    GIVEN a Profile with a date of birth
    WHEN age is calculated
    THEN check the age is correct
    """
    profile = Profile(
        user_id=1,
        first_name='John',
        last_name='Doe',
        state='CA',
        filing_status='single',
        income_type='Salary',
        pay_cycle='biweekly',
        retirement_contribution_type='pretax',
        date_of_birth=date(1990, 1, 1)
    )
    # Note: This test will need to be updated yearly
    expected_age = datetime.now().year - 1990
    assert profile.age == expected_age

def test_budget_creation():
    """
    GIVEN a Budget model
    WHEN a new Budget is created
    THEN check all fields are set correctly
    """
    budget = Budget(
        user_id=1,
        profile_id=1,
        name='Monthly Budget',
        gross_income=50000
    )
    assert budget.name == 'Monthly Budget'
    assert budget.gross_income == 50000
    assert budget.status == 'draft'
    assert isinstance(budget.created_at, datetime)
    assert isinstance(budget.updated_at, datetime)

def test_budget_summary():
    """
    GIVEN a Budget with income sources
    WHEN get_budget_summary is called
    THEN check the summary is correct
    """
    budget = Budget(
        user_id=1,
        profile_id=1,
        name='Test Budget',
        gross_income=50000,
        status='draft'
    )
    summary = budget.get_budget_summary()
    assert summary['name'] == 'Test Budget'
    assert summary['status'] == 'draft'
    assert isinstance(summary['created_at'], str)
    assert isinstance(summary['updated_at'], str) 