"""backend/app/auth/routes.py"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm
from app.models import User
from app import db, bcrypt
from app.auth.email_service import email_service
from app.auth.rate_limiter import rate_limiter


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Create new user (User model hashes the password)
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            db.session.add(new_user)
            db.session.commit()

            flash('Account created successfully. You can now log in.', 'success')
            return redirect(url_for('auth.login'))

        except IntegrityError:
            db.session.rollback()
            flash('An account with this email already exists. Please log in.', 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)




@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if request.method == "POST" and not form.validate_on_submit():
        print(f"❌ Form validation failed: {form.errors}")

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # Debugging information
        print(f"DEBUG: Attempting login for email: {form.email.data}")

        if not user:
            print("❌ No user found with this email.")
            flash("No account found with that email.", "danger")
            return redirect(url_for("auth.login"))

        print(f"DEBUG: Found user {user.email}, checking password...")

        # FIXED: Use `password_hash` instead of `password`
        if not bcrypt.check_password_hash(user.password_hash, form.password.data):  
            print("❌ Password mismatch.")
            flash("Incorrect password. Try again.", "danger")
            return redirect(url_for("auth.login"))

        # Successful login
        login_user(user, remember=form.remember_me.data)
        print(f"✅ User {user.email} logged in successfully!")

        flash("Login successful!", "success")
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))

    return render_template('auth/login.html', form=form)



@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def request_password_reset():
    """Handle password reset request."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        
        # Check rate limiting
        if rate_limiter.is_rate_limited(email):
            remaining_time = rate_limiter.get_remaining_time(email)
            minutes = remaining_time // 60
            flash(f'Too many reset requests. Please wait {minutes} minutes before trying again.', 'danger')
            return render_template('auth/reset_password_request.html', form=form)
        
        # Check if user exists (but don't reveal this)
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            token = email_service.generate_reset_token(email)
            
            # Create reset URL
            base_url = request.host_url.rstrip('/')
            reset_url = f"{base_url}/auth/reset-password/{token}"
            
            # Send email
            if email_service.send_password_reset_email(email, reset_url):
                flash('Password reset instructions have been sent to your email.', 'success')
            else:
                flash('Failed to send reset email. Please try again later.', 'danger')
        else:
            # Always show success message for security (prevents email enumeration)
            flash('Password reset instructions have been sent to your email.', 'success')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Verify token
    email = email_service.verify_reset_token(token)
    if not email:
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Invalid reset link.', 'danger')
        return redirect(url_for('auth.login'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        # Update password
        user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        
        flash('Your password has been reset successfully. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form, token=token)
