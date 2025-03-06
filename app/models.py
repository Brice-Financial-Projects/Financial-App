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
    income_type = db.Column(db.String(20), nullable=False)
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
    gross_income = db.Column(db.Float, nullable=False, default=0.0)
    tax_withholding = db.Column(db.Float, default=0)
    retirement_contribution = db.Column(db.Float, default=0)
    benefit_deductions = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    other_income_sources = db.Column(JSON, nullable=True)

    # Relationships
    user = db.relationship("User", back_populates="budgets")
    profile = db.relationship("Profile", back_populates="budgets")
    budget_items = db.relationship("BudgetItem", back_populates="budget", cascade="all, delete-orphan")

    @property
    def income_type(self):
        return self.user.profile.income_type if self.user and self.user.profile else "Salary"

    @property
    def state(self):
        return self.user.profile.state if self.user and self.user.profile else "CA"

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

