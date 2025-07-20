# 🔧 Password Reset Flow – Design Questions

To implement a secure and user-friendly password reset flow using `itsdangerous` and SendGrid, the following design considerations need to be addressed:

---

## ⏳ Token Expiration
**Question:**  
How long should the password reset token be valid?

**Options:**  
Response: **- 1 hour (default industry standard)**
- 24 hours
- 7 days

---

## 💌 Email Template
**Question:**  
What type of email template should be used for the reset email?

**Options:**  
Response: **- Simple HTML template (minimal formatting)**
- Styled HTML template with app branding

---

## 🔁 Reset Flow Structure
**Question:**  
Which password reset flow should be used?

**Options:**  
1. **Recommended:**
   - User enters email
   - Reset link is sent via email
   - User clicks link → New password form is displayed

2. **Alternative (less common):**
   - User enters email
   - Reset link is sent via email
   - User clicks link → Must enter current password + new password

## Response
**USE Number 1 Option**

---

## 🔐 Password Requirements
**Question:**  
Should the new password follow the same validation rules as registration?

**Options:**  
Response: **- Yes (reuse `password_check` validator)**
- No (simplified rules for reset)

---

## 📉 Rate Limiting
**Question:**  
Should rate limiting be applied to password reset requests?

**Options:**  
Response: **- Yes (e.g., max 3 requests/hour per email)**
- No (no rate limit)

---

## ✅ Success & Error Handling
**Questions:**
1. Should we always show **"Email sent"**, even if the email is not found in the system?  
   *(Security best practice to prevent account enumeration)*

2. After a successful password reset, should the user be **redirected to the login page**?

## Response
**Yes to both 1 and 2**

---

## 📬 SendGrid Configuration
**Question:**  
Should the implementation include SendGrid setup code?

**Options:**  
- Yes (integrate SendGrid client and email sender)
- No (handled separately by environment setup)


## 📬 SendGrid Configuration
**Decision:**  
✅ Yes — include full SendGrid integration code for sending password reset emails.  
The API key will be securely loaded via environment variables (e.g., `.env` file).

---

## 🛠️ Planned Implementation Components
- `PasswordResetRequestForm` – Form to submit email for reset
- `PasswordResetForm` – Form to enter new password
- `request_password_reset()` – Route to handle email submission
- `reset_password()` – Route to handle token validation and update password
- HTML email template with secure reset link
- Token generation & validation using `itsdangerous`
