"""Test profile routes and functionality."""
import pytest
from flask import url_for

def test_profile_page(auth_client, test_profile):
    """Test profile page loads."""
    response = auth_client.get('/profile')
    assert response.status_code == 200
    assert b'Test User' in response.data
    assert b'CA' in response.data

def test_create_profile(auth_client):
    """Test profile creation."""
    response = auth_client.post('/profile/create', data={
        'first_name': 'John',
        'last_name': 'Doe',
        'state': 'NY',
        'retirement_contribution': 5000,
        'retirement_contribution_type': 'pretax',
        'health_insurance_premium': 2000,
        'hsa_contribution': 1000,
        'fsa_contribution': 500,
        'other_pretax_benefits': 1000,
        'federal_additional_withholding': 100,
        'state_additional_withholding': 50
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'John Doe' in response.data
    assert b'NY' in response.data

def test_update_profile(auth_client, test_profile):
    """Test profile update."""
    response = auth_client.post('/profile/update', data={
        'first_name': 'Jane',
        'last_name': 'Smith',
        'state': 'CA',
        'retirement_contribution': 6000,
        'retirement_contribution_type': 'pretax',
        'health_insurance_premium': 2500,
        'hsa_contribution': 1200,
        'fsa_contribution': 600,
        'other_pretax_benefits': 1200,
        'federal_additional_withholding': 150,
        'state_additional_withholding': 75
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Jane Smith' in response.data
    assert b'CA' in response.data
    assert b'6000' in response.data
    assert b'2500' in response.data

def test_profile_form_validation(auth_client):
    """Test profile form validation."""
    response = auth_client.post('/profile/create', data={
        'first_name': '',  # Empty first name should fail validation
        'last_name': '',   # Empty last name should fail validation
        'state': 'XXX',   # Invalid state code
        'retirement_contribution': -1000,  # Negative value should fail validation
        'health_insurance_premium': -500   # Negative value should fail validation
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'First Name' in response.data
    assert b'Last Name' in response.data
    assert b'State Code' in response.data
    assert b'Retirement Contribution' in response.data
    assert b'Health Insurance Premium' in response.data

def test_profile_required_fields(auth_client):
    """Test that required profile fields are enforced."""
    response = auth_client.post('/profile/create', data={
        'first_name': 'John',
        'last_name': 'Doe'
        # Missing required state field
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'State is required' in response.data

def test_profile_retirement_contribution_types(auth_client):
    """Test retirement contribution type validation."""
    response = auth_client.post('/profile/create', data={
        'first_name': 'John',
        'last_name': 'Doe',
        'state': 'NY',
        'retirement_contribution': 5000,
        'retirement_contribution_type': 'invalid_type'  # Invalid contribution type
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid retirement contribution type' in response.data 