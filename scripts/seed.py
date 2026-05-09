"""
seed.py
--------
Idempotent seed script for BudgetSync (Turso)
"""

import os
from budget_sync import create_app, db
from budget_sync.models import (
    User,
    Profile,
    ExpenseCategory,
    ExpenseTemplate,
)

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not ADMIN_EMAIL or not ADMIN_PASSWORD:
    raise RuntimeError(
        "ADMIN_EMAIL and ADMIN_PASSWORD must be set in the environment before running seed.py"
    )


def seed_admin_user():
    user = User.query.filter_by(email=ADMIN_EMAIL).first()
    if user:
        return user

    user = User(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD
    )
    user.is_admin = True
    db.session.add(user)
    db.session.commit()
    return user


def seed_admin_profile(user):
    profile = Profile.query.filter_by(user_id=user.id).first()
    if profile:
        return profile

    profile = Profile(
        user_id=user.id,
        first_name="Admin",
        last_name="User",
        state="CA",
        filing_status="single",
        num_dependents=0,
        income_type="Salary",
        pay_cycle="monthly",
        retirement_contribution_type="pretax"
    )

    db.session.add(profile)
    db.session.commit()
    return profile


def seed_expense_categories():
    categories = [
        ("Housing", "Rent, mortgage, HOA"),
        ("Utilities", "Electric, water, gas"),
        ("Transportation", "Car, gas, transit"),
        ("Food", "Groceries and dining"),
        ("Insurance", "Health, auto, life"),
        ("Debt", "Loans and credit cards"),
        ("Savings", "Emergency and long-term savings"),
        ("Entertainment", "Subscriptions and fun"),
    ]

    for priority, (name, desc) in enumerate(categories):
        exists = ExpenseCategory.query.filter_by(name=name).first()
        if not exists:
            db.session.add(
                ExpenseCategory(
                    name=name,
                    description=desc,
                    priority=priority
                )
            )

    db.session.commit()


def seed_expense_templates():
    templates = {
        "Housing": ["Rent / Mortgage"],
        "Utilities": ["Electric", "Water", "Internet"],
        "Transportation": ["Car Payment", "Fuel"],
        "Food": ["Groceries", "Dining Out"],
        "Insurance": ["Health Insurance", "Auto Insurance"],
        "Debt": ["Credit Card", "Student Loan"],
        "Savings": ["Emergency Fund"],
        "Entertainment": ["Streaming Services"],
    }

    for category_name, items in templates.items():
        category = ExpenseCategory.query.filter_by(name=category_name).first()
        if not category:
            continue

        for priority, name in enumerate(items):
            exists = ExpenseTemplate.query.filter_by(
                name=name,
                category_id=category.id
            ).first()
            if not exists:
                db.session.add(
                    ExpenseTemplate(
                        category_id=category.id,
                        name=name,
                        is_default=True,
                        priority=priority
                    )
                )

    db.session.commit()


def run():
    app = create_app()
    with app.app_context():
        admin = seed_admin_user()
        seed_admin_profile(admin)
        seed_expense_categories()
        seed_expense_templates()
        print("✅ Database seeded successfully.")


if __name__ == "__main__":
    run()
