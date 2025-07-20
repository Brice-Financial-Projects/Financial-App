# Authentication System Documentation

## Overview

The authentication system provides secure user registration, login, logout, and password reset functionality using Flask-Login with server-side sessions and bcrypt password hashing.

## Features

### ✅ Implemented Features
- **User Registration** - Secure account creation with email validation
- **User Login/Logout** - Session-based authentication with "Remember Me"
- **Password Reset** - Secure token-based password reset via email
- **Password Security** - Strong password requirements with bcrypt hashing
- **Rate Limiting** - Redis-based rate limiting for password reset requests
- **CSRF Protection** - Built-in CSRF protection with Flask-WTF
- **Session Management** - Redis in production, filesystem in development

### 🔄 Authentication Flow

#### Registration Flow
1. User visits `/auth/register`
2. User fills out registration form (username, email, password)
3. Password is validated and hashed with bcrypt
4. User account is created in database
5. User is redirected to login page

#### Login Flow
1. User visits `/auth/login`
2. User enters email and password
3. Password is verified against bcrypt hash
4. Flask-Login creates server-side session
5. User is redirected to dashboard

#### Password Reset Flow
1. User clicks "Forgot your password?" on login page
2. User enters email address on reset request form
3. System checks rate limiting (max 3 requests/hour)
4. If user exists, secure token is generated and email sent
5. User clicks link in email (valid for 1 hour)
6. User enters new password with validation
7. Password is updated and user redirected to login

## Security Features

### Password Requirements
- Minimum 16 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character

### Rate Limiting
- **Password Reset Requests**: 3 requests per hour per email address
- **Storage**: Redis (with fallback to no rate limiting if Redis unavailable)
- **Key Format**: `password_reset:{email}`

### Token Security
- **Generation**: Uses `itsdangerous.URLSafeTimedSerializer`
- **Expiration**: 1 hour (3600 seconds)
- **Salt**: `password-reset-salt` (prevents token reuse)
- **Secret**: Uses Flask app's `SECRET_KEY`

### Session Security
- **CSRF Protection**: Enabled with Flask-WTF
- **Session Storage**: Redis in production, filesystem in development
- **Session Type**: Server-side sessions (not JWT)

## File Structure

```
app/auth/
├── __init__.py              # Blueprint initialization
├── forms.py                 # WTForms for authentication
├── routes.py                # Authentication routes
├── email_service.py         # SendGrid email service
├── rate_limiter.py          # Redis rate limiting
├── README-auth.md           # This documentation
└── templates/
    ├── login.html           # Login form
    ├── register.html        # Registration form
    ├── reset_password_request.html  # Password reset request
    └── reset_password.html  # Password reset form
```

## Routes

| Route | Methods | Description |
|-------|---------|-------------|
| `/auth/register` | GET, POST | User registration |
| `/auth/login` | GET, POST | User login |
| `/auth/logout` | GET | User logout |
| `/auth/reset-password` | GET, POST | Request password reset |
| `/auth/reset-password/<token>` | GET, POST | Reset password with token |

## Forms

### LoginForm
- `email` - User's email address
- `password` - User's password
- `remember_me` - Remember user session

### RegistrationForm
- `username` - Unique username
- `email` - Unique email address
- `password` - Strong password
- `confirm_password` - Password confirmation

### PasswordResetRequestForm
- `email` - Email address for reset

### PasswordResetForm
- `password` - New password
- `confirm_password` - Password confirmation

## Email Service

### SendGrid Integration
- **From Email**: `brice@devbybrice.com`
- **Display Name**: "Budget Sync Support"
- **Subject**: "Password Reset Request - Budget Sync"
- **Template**: Simple HTML with reset button

### Email Template Features
- Responsive design with Bootstrap styling
- Clear call-to-action button
- Fallback text link
- Security warnings and expiration notice
- Professional branding

## Rate Limiting

### Implementation
- Uses Redis for persistent storage
- Graceful fallback if Redis unavailable
- Configurable limits and time windows

### Configuration
- **Max Requests**: 3 per hour per email
- **Time Window**: 1 hour (3600 seconds)
- **Key Pattern**: `password_reset:{email}`

## Environment Variables

### Required
```env
# SendGrid Configuration
SENDGRID_API_KEY=your_sendgrid_api_key

# Flask Configuration
SECRET_KEY=your_secret_key

# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis (for sessions and rate limiting)
REDIS_URL=redis://localhost:6379/0
```

### Optional
```env
# Production base URL for reset links
APP_BASE_URL=https://yourapp.com

# Session configuration
SESSION_TYPE=redis  # or filesystem
```

## Testing

### Functional Tests
- Password reset request flow
- Token validation and expiration
- Rate limiting behavior
- Form validation
- Security features

### Test Coverage
- Valid and invalid email addresses
- Strong and weak passwords
- Valid and invalid tokens
- Rate limiting scenarios
- Error handling

## Security Best Practices

### Implemented
- ✅ Password hashing with bcrypt
- ✅ CSRF protection on all forms
- ✅ Rate limiting for password reset
- ✅ Secure token generation with expiration
- ✅ No email enumeration (always show success)
- ✅ Strong password requirements
- ✅ Session-based authentication
- ✅ Input validation and sanitization

### Recommendations
- Set strong `SECRET_KEY` in production
- Use HTTPS in production
- Monitor rate limiting logs
- Regular security audits
- Keep dependencies updated

## Dependencies

### Core Authentication
- `Flask-Login` - Session management
- `Flask-Bcrypt` - Password hashing
- `Flask-WTF` - Form handling and CSRF
- `Flask-Session` - Session storage

### Password Reset
- `SendGrid` - Email delivery
- `itsdangerous` - Secure token generation
- `redis` - Rate limiting storage

## Troubleshooting

### Common Issues

#### Email Not Sending
- Check `SENDGRID_API_KEY` environment variable
- Verify SendGrid account and API key permissions
- Check application logs for error messages

#### Rate Limiting Not Working
- Verify Redis connection and `REDIS_URL`
- Check if Redis service is running
- Review rate limiting logs

#### Token Expiration Issues
- Verify `SECRET_KEY` is consistent across deployments
- Check system time synchronization
- Review token generation/validation logic

#### Session Issues
- Verify `SESSION_TYPE` configuration
- Check Redis connection for production
- Review session storage permissions

## Future Enhancements

### Potential Improvements
- Email verification for new accounts
- Two-factor authentication (2FA)
- Account lockout after failed attempts
- Password history tracking
- Social login integration
- JWT tokens for API access
- Enhanced audit logging

### Monitoring
- Failed login attempt tracking
- Password reset request monitoring
- Rate limiting analytics
- Security event logging 