# Registration Email Confirmation Flow

This document outlines the email confirmation flow for user registration in the Budget Sync application. It describes the process of sending a confirmation email to the user, verifying the token, and updating the user's account status upon successful confirmation.

```graphviz
User opens /register page
         |
         v
  Fills RegistrationForm
         |
         v
 form.validate_on_submit() checks form validity
         |
         v
  1️⃣ IP Throttling (auth/routes.py)
     - Check TesterLog for recent signups from request.remote_addr
     - If >= 5 in last hour -> reject
         |
         v
  2️⃣ Create new User (auth/routes.py)
     - new_user = User(username, email, password, confirmed=False)
     - db.session.add(new_user)
     - db.session.flush()  # ensures new_user.id exists
         |
         v
  3️⃣ Log IP (auth/routes.py)
     - log = TesterLog(user_id=new_user.id, ip=request.remote_addr)
     - db.session.add(log)
         |
         v
  4️⃣ Generate email confirmation token (auth/routes.py)
     - s = URLSafeTimedSerializer(app.SECRET_KEY)
     - token = s.dumps(new_user.email, salt="email-confirm")
     - confirm_url = url_for('auth.confirm_email', token=token, _external=True)
         |
         v
  5️⃣ Send email (utils/email.py)
     - send_confirmation_email(new_user.email, confirm_url)
         |
         v
  6️⃣ Commit everything to DB (auth/routes.py)
     - db.session.commit()
         |
         v
  Flash message: "Check your email to confirm your account."
         |
         v
-------------------- EMAIL --------------------
User receives email with confirm_url link
         |
         v
User clicks link -> GET /confirm_email/<token> (auth/routes.py)
         |
         v
  7️⃣ Token verification
     - s.loads(token, salt="email-confirm", max_age=3600)
     - Errors: SignatureExpired, BadSignature
         |
         v
  8️⃣ Lookup user by email
         |
         v
  9️⃣ Set confirmed=True
     - db.session.commit()
         |
         v
  Flash message: "Email confirmed! You can now log in."
         |
         v
User redirected to /login
         |
         v
Login route checks:
     - if user.confirmed == False -> block login
     - if confirmed -> allow login
```

---

## Flow Breakdown
| Step | Feature                     | File                                         |
| ---- | --------------------------- | -------------------------------------------- |
| 1    | IP throttling               | `auth/routes.py` (register route)            |
| 2    | Create new user             | `auth/routes.py` (register route)            |
| 3    | Log IP                      | `auth/routes.py` (register route)            |
| 4    | Generate confirmation token | `auth/routes.py` (register route)            |
| 5    | Send email                  | `utils/email.py` or your email helper module |
| 6    | Commit user + log           | `auth/routes.py` (register route)            |
| 7    | Token verification          | `auth/routes.py` (confirm_email route)       |
| 8    | Lookup user by email        | `auth/routes.py` (confirm_email route)       |
| 9    | Set confirmed=True          | `auth/routes.py` (confirm_email route)       |
| 10   | Login check                 | `auth/routes.py` (login route)               |

---

## Notes / Best Practices
- Flush vs Commit: db.session.flush() allows logging the IP using new_user.id before commit, preventing errors.
- confirmed=False: ensures users cannot log in until they click the link.
- Email token max_age: 1 hour in example, adjustable if you want more time.
- IP logging: helps prevent spam / bot signups even though DB is open (0.0.0.0/0).
- Login route: must enforce confirmed=True to complete the flow.