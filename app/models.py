"""backend/app/models.py"""

from app import bcrypt, db
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON


# -------------------- User Model --------------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    profile = db.relationship("Profile", back_populates="user", uselist=False)
    budgets = db.relationship("Budget", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        # Hash the password using bcrypt
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # Flask-Login required properties:
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<User {self.username}, {self.email}>"

# -------------------- Profile Model --------------------
class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    income_type = db.Column(db.String(20), nullable=False, default="Salary")  # ✅ Reverting back
    tax_withholding = db.Column(db.Float, default=0)
    retirement_contribution_type = db.Column(db.String(10), nullable=False)
    retirement_contribution = db.Column(db.Float, default=0)
    pay_cycle = db.Column(db.String(20), nullable=False)
    benefit_deductions = db.Column(db.Float, default=0)

    # Relationships
    user = db.relationship("User", back_populates="profile")
    budgets = db.relationship("Budget", back_populates="profile")

    def __repr__(self):
        return f"<Profile {self.first_name} {self.last_name}, State: {self.state}>"




# -------------------- Budget Model --------------------
class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    # Primary salary details are stored in Profile
    gross_income = db.Column(db.Float, nullable=False, default=0.0)  # 💰 Consistency in naming
    retirement_contribution = db.Column(db.Float, default=0)
    benefit_deductions = db.Column(db.Float, default=0)

    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    # Relationships
    user = db.relationship("User", back_populates="budgets")
    profile = db.relationship("Profile", back_populates="budgets")
    budget_items = db.relationship("BudgetItem", back_populates="budget", cascade="all, delete-orphan")
    gross_income_sources = db.relationship("GrossIncome", back_populates="budget", cascade="all, delete-orphan")  # 🔄 Updated reference

    @property
    def salary_type(self):
        return self.user.profile.salary_type if self.user and self.user.profile else "Salary"

    @property
    def state(self):
        return self.user.profile.state if self.user and self.user.profile else "CA"

    @property
    def tax_withholding(self):
        """Pull tax withholding from Profile instead of duplicating."""
        return self.user.profile.tax_withholding if self.user and self.user.profile else 0

    def __repr__(self):
        return f"<Budget {self.name}>"



# -------------------- BudgetItem Model --------------------
class BudgetItem(db.Model):
    __tablename__ = "budget_items"

    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    minimum_payment = db.Column(db.Float, nullable=False, default=0.0)
    preferred_payment = db.Column(db.Float, nullable=False, default=0.0)

    # Relationship
    budget = db.relationship("Budget", back_populates="budget_items")

    def __repr__(self):
        return f"<BudgetItem {self.category} - {self.name}>"


# -------------------- Gross Income Model ------------------------------
class GrossIncome(db.Model):
    __tablename__ = "gross_income"

    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., "W2 Job", "Rental", "Freelance"
    source = db.Column(db.String(100), nullable=False)  # e.g., "Uber", "Book Royalties"
    gross_income = db.Column(db.Float, nullable=False)  # 💰 Clearly labeled as "Gross"
    frequency = db.Column(db.String(20), nullable=False, default="monthly")  # e.g., "weekly", "monthly"

    # ✅ Reference tax rules dynamically
    tax_type = db.Column(db.String(50), nullable=False)  # "W2", "Self-Employed", "Capital Gains", "Rental"
    state_tax_ref = db.Column(db.String(2), nullable=True)  # Used for API calls based on Profile.state

    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    # Relationship
    budget = db.relationship("Budget", back_populates="gross_income_sources")

    def __repr__(self):
        return f"<GrossIncome {self.source} - ${self.gross_income} ({self.frequency}) - Tax: {self.tax_type}, State Tax: {self.state_tax_ref}>"

