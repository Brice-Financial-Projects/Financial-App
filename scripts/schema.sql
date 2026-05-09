-- ================================
-- BudgetSync Schema (Turso / SQLite)
-- ================================

PRAGMA foreign_keys = ON;

-- --------------------
-- Users
-- --------------------
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN NOT NULL DEFAULT 0
);

-- --------------------
-- Profiles
-- --------------------
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,

    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth DATE,
    is_blind BOOLEAN NOT NULL DEFAULT 0,
    is_student BOOLEAN NOT NULL DEFAULT 0,

    state TEXT NOT NULL,
    filing_status TEXT NOT NULL DEFAULT 'single',
    num_dependents INTEGER NOT NULL DEFAULT 0,

    income_type TEXT NOT NULL DEFAULT 'Salary',
    pay_cycle TEXT NOT NULL,

    federal_additional_withholding REAL NOT NULL DEFAULT 0.0,
    state_additional_withholding REAL NOT NULL DEFAULT 0.0,

    retirement_contribution_type TEXT NOT NULL,
    retirement_contribution REAL NOT NULL DEFAULT 0.0,

    health_insurance_premium REAL NOT NULL DEFAULT 0.0,
    hsa_contribution REAL NOT NULL DEFAULT 0.0,
    fsa_contribution REAL NOT NULL DEFAULT 0.0,
    other_pretax_benefits REAL NOT NULL DEFAULT 0.0,
    benefit_deductions REAL NOT NULL DEFAULT 0.0,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- --------------------
-- Password Reset Tokens
-- --------------------
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    used BOOLEAN NOT NULL DEFAULT 0,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- --------------------
-- Budgets
-- --------------------
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    profile_id INTEGER NOT NULL,
    name TEXT NOT NULL,

    gross_income REAL NOT NULL DEFAULT 0.0,
    retirement_contribution REAL NOT NULL DEFAULT 0.0,
    benefit_deductions REAL NOT NULL DEFAULT 0.0,

    status TEXT NOT NULL DEFAULT 'draft',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (user_id, name),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

-- --------------------
-- Expense Categories
-- --------------------
CREATE TABLE IF NOT EXISTS expense_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    priority INTEGER NOT NULL DEFAULT 0
);

-- --------------------
-- Expense Templates
-- --------------------
CREATE TABLE IF NOT EXISTS expense_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    is_default BOOLEAN NOT NULL DEFAULT 0,
    priority INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (category_id) REFERENCES expense_categories(id) ON DELETE CASCADE
);

-- --------------------
-- Budget Items
-- --------------------
CREATE TABLE IF NOT EXISTS budget_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    minimum_payment REAL NOT NULL DEFAULT 0.0,
    preferred_payment REAL NOT NULL DEFAULT 0.0,
    template_id INTEGER,

    FOREIGN KEY (budget_id) REFERENCES budgets(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES expense_templates(id)
);

-- --------------------
-- Gross Income
-- --------------------
CREATE TABLE IF NOT EXISTS gross_income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    source TEXT NOT NULL,
    gross_income REAL NOT NULL,
    frequency TEXT NOT NULL DEFAULT 'monthly',
    tax_type TEXT NOT NULL,
    state_tax_ref TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (budget_id) REFERENCES budgets(id) ON DELETE CASCADE
);

-- --------------------
-- Other Income
-- --------------------
CREATE TABLE IF NOT EXISTS other_income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    source TEXT NOT NULL,
    amount REAL NOT NULL,
    frequency TEXT NOT NULL DEFAULT 'monthly',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (budget_id) REFERENCES budgets(id) ON DELETE CASCADE
);
