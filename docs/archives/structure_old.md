# structure (OLD)

flask_budget_app/
│
├── app/
│   ├── __init__.py           # Initialize Flask app and extensions
│   ├── models.py             # General SQLAlchemy models
│   ├── forms.py              # General WTForms for shared functionality
|	├── config/
|	│   ├── __init__.py       # Makes the config folder a package
|	│   └── settings.py       # Configuration classes for different environments
|	|
│   ├── config.py             # General application configuration
│   ├── templates/            # Shared HTML templates
│   │   ├── base.html         # Base template for layout
│   │   └── general.html      # General/shared templates
│   ├── static/               # Shared static files (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── budget/               # Budget-specific functionality
│   │   ├── __init__.py       # Init file for the budget module
│   │   ├── routes.py         # Budget-specific routes
│   │   ├── utils.py          # Budget-specific utility functions
│   │   ├── models.py         # Budget-specific models (if any)
│   │   ├── forms.py          # Budget-specific forms
│   │   └── templates/        # Budget-specific templates
│   │       ├── form.html     # Form for budget input
│   │       └── dashboard.html# Dashboard for budgets
│   ├── debt/                 # Debt-specific functionality
│   │   ├── __init__.py       # Init file for the debt module
│   │   ├── routes.py         # Debt-specific routes
│   │   ├── utils.py          # Debt-specific utility functions
│   │   ├── models.py         # Debt-specific models (if any)
│   │   ├── forms.py          # Debt-specific forms
│   │   └── templates/        # Debt-specific templates
│   │       ├── payoff.html   # Recommended debt payoff strategy
│   │       └── overview.html # Debt overview template
│
├── migrations/               # Alembic migration files
│
├── tests/
│   ├── __init__.py           # Test initialization
│   ├── test_budget.py        # Tests for budget functionality
│   ├── test_debt.py          # Tests for debt functionality
│   └── test_general.py       # Tests for shared/general functionality
│
├── .env                      # Environment variables (e.g., DB credentials)
├── .gitignore                # Git ignore file
├── requirements.txt          # Python dependencies
├── run.py                    # Entry point to run the app
|── documentation.md          # Project documentation and details
|
└── README.md                 # Project documentation

