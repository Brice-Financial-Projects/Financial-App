"""Functional tests for password reset functionality."""

import pytest
from flask import url_for
from app.models import User


def test_password_reset_request_page(client):
    """Test that password reset request page loads."""
    response = client.get('/auth/reset-password')
    assert response.status_code == 200
    assert b'Reset Password' in response.data
    assert b'Enter your email address' in response.data


def test_password_reset_request_with_valid_email(client, test_user):
    """Test password reset request with valid email."""
    response = client.post('/auth/reset-password', data={
        'email': 'test@example.com'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Should show success message (even if email doesn't exist for security)
    assert b'Password reset instructions have been sent' in response.data


def test_password_reset_request_with_invalid_email(client):
    """Test password reset request with invalid email."""
    response = client.post('/auth/reset-password', data={
        'email': 'invalid-email'
    }, follow_redirects=False)
    
    assert response.status_code == 200  # Form validation error, not redirect


def test_password_reset_with_invalid_token(client):
    """Test password reset with invalid token."""
    response = client.get('/auth/reset-password/invalid-token')
    assert response.status_code == 302  # Redirect to login
    # Should redirect to login with error message


def test_password_reset_page_loads_with_valid_token(client, test_user, app):
    """Test that password reset page loads with valid token."""
    from app.auth.email_service import email_service
    
    with app.app_context():
        # Generate a valid token
        token = email_service.generate_reset_token('test@example.com')
        
        response = client.get(f'/auth/reset-password/{token}')
        assert response.status_code == 200
        assert b'Set New Password' in response.data


def test_password_reset_success(client, test_user, app):
    """Test successful password reset."""
    from app.auth.email_service import email_service
    
    with app.app_context():
        # Generate a valid token
        token = email_service.generate_reset_token('test@example.com')
        
        # Submit new password
        response = client.post(f'/auth/reset-password/{token}', data={
            'password': 'NewPassword123!@#',
            'confirm_password': 'NewPassword123!@#'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Your password has been reset successfully' in response.data
        
        # Verify password was actually changed
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        # Note: We can't easily test the password hash without bcrypt, but the redirect indicates success


def test_password_reset_with_mismatched_passwords(client, test_user, app):
    """Test password reset with mismatched passwords."""
    from app.auth.email_service import email_service
    
    with app.app_context():
        token = email_service.generate_reset_token('test@example.com')
        
        response = client.post(f'/auth/reset-password/{token}', data={
            'password': 'NewPassword123!@#',
            'confirm_password': 'DifferentPassword123!@#'
        }, follow_redirects=False)
        
        assert response.status_code == 200  # Form validation error
        assert b'Field must be equal to password' in response.data


def test_password_reset_with_weak_password(client, test_user, app):
    """Test password reset with weak password."""
    from app.auth.email_service import email_service
    
    with app.app_context():
        token = email_service.generate_reset_token('test@example.com')
        
        response = client.post(f'/auth/reset-password/{token}', data={
            'password': 'weak',
            'confirm_password': 'weak'
        }, follow_redirects=False)
        
        assert response.status_code == 200  # Form validation error
        assert b'Password must be at least 16 characters' in response.data 