"""Email service for password reset functionality."""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from flask import current_app, request
from itsdangerous import URLSafeTimedSerializer


class EmailService:
    """Service for sending emails via SendGrid."""
    
    def __init__(self):
        self.sg = SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
        self.serializer = None  # Will be initialized when needed
    
    def _get_serializer(self):
        """Get serializer with current app context."""
        if self.serializer is None:
            self.serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return self.serializer
    
    def generate_reset_token(self, email):
        """Generate a secure token for password reset."""
        serializer = self._get_serializer()
        return serializer.dumps(email, salt='password-reset-salt')
    
    def verify_reset_token(self, token, expiration=3600):
        """Verify the reset token and return the email if valid."""
        try:
            serializer = self._get_serializer()
            email = serializer.loads(
                token, 
                salt='password-reset-salt', 
                max_age=expiration
            )
            return email
        except:
            return None
    
    def send_password_reset_email(self, email, reset_url):
        """Send password reset email via SendGrid."""
        
        # Determine base URL for production vs development
        base_url = os.getenv('APP_BASE_URL')
        if not base_url:
            base_url = request.host_url.rstrip('/')
        
        # Email content
        subject = "Password Reset Request - Budget Sync"
        
        html_content = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hello,</p>
            <p>You recently requested to reset your password for your Budget Sync account.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p>{reset_url}</p>
            <p><strong>This link will expire in 1 hour.</strong></p>
            <p>If you didn't request this password reset, please ignore this email.</p>
            <p>Best regards,<br>Budget Sync Support</p>
        </body>
        </html>
        """
        
        # Create email
        from_email = Email("brice@devbybrice.com", "Budget Sync Support")
        to_email = To(email)
        content = Content("text/html", html_content)
        mail = Mail(from_email, to_email, subject, content)
        
        try:
            response = self.sg.send(mail)
            return response.status_code == 202
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {e}")
            return False


# Global email service instance
email_service = EmailService() 