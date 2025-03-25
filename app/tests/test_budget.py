"""Test budget routes and functionality."""
import pytest
from flask import url_for

def test_budget_dashboard(auth_client, test_budget):
    """Test budget dashboard loads."""
    response = auth_client.get('/')
    assert response.status_code == 200
    assert b'Test Budget' in response.data

def test_create_budget(auth_client):
    """Test budget creation."""
    response = auth_client.post('/budget/create', data={
        'budget_name': 'New Budget'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'New Budget' in response.data

def test_view_budget(auth_client, test_budget):
    """Test viewing a budget."""
    response = auth_client.get(f'/budget/{test_budget.id}')
    assert response.status_code == 200
    assert b'Test Budget' in response.data

def test_delete_budget(auth_client, test_budget):
    """Test budget deletion."""
    response = auth_client.post(f'/budget/{test_budget.id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Test Budget' not in response.data

def test_budget_calculation(auth_client, test_budget, test_profile):
    """Test basic budget calculation."""
    # Add some test data to the budget
    test_budget.gross_income = 50000
    test_budget.state = 'CA'
    test_profile.retirement_contribution = 5000
    test_profile.benefit_deductions = 2000
    
    response = auth_client.post(f'/budget/{test_budget.id}/calculate', follow_redirects=True)
    assert response.status_code == 200
    assert b'Budget Results' in response.data 