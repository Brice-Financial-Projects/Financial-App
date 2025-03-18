# Project Structure with Just Backend Flask

flask_budget_app/
├── app/
│   ├── __init__.py        # Initialize the Flask app and extensions
│   ├── models.py          # Database models for budgets, users, profiles, and income
│   ├── main/              # Main blueprint for core functionality
│   │   ├── __init__.py    # Initialize main blueprint
│   │   ├── routes.py      # Main app routes (homepage, dashboard, etc.)
│   ├── auth/              # Authentication blueprint
│   │   ├── __init__.py    # Blueprint for authentication
│   │   ├── routes.py      # Login, logout, registration routes
│   │   ├── forms.py       # Auth forms (Login, Register)
│   ├── profile/           # User profile blueprint
│   │   ├── __init__.py    # Blueprint for profile routes
│   │   ├── routes.py      # Profile routes with tax info handling
│   │   ├── forms.py       # Profile forms with tax-related fields
│   ├── budget/            # Budget blueprint
│   │   ├── __init__.py    # Blueprint for budget routes
│   │   ├── routes.py      # Budget routes (create, input, income, preview, calculate)
│   │   ├── budget_logic.py # Budget calculations and logic
│   │   ├── tax_api.py     # Interface between budget and tax rate API
│   ├── api/               # API integrations and services
│   │   ├── __init__.py    # API package initialization
│   │   ├── tax_rates/     # Tax rate calculation APIs
│   │   │   ├── __init__.py # Tax rates package initialization
│   │   │   ├── client.py  # Tax API client implementation
│   │   │   ├── models.py  # Tax bracket and calculation models
│   │   │   ├── config.py  # API configuration settings
│   │   │   ├── cache.py   # Cache implementation for tax data
│   │   │   ├── data/      # Sample tax data for testing
│   │   │   │   ├── federal_tax_data.py # Federal tax brackets
│   │   │   │   ├── state_tax_data.py   # State tax rates
│   │   │   │   ├── fica_tax_data.py    # FICA tax rates
│   │   ├── services.py    # Common API service functions
│   │   ├── errors.py      # API error handling utilities
│   ├── templates/         # HTML templates
│   │   ├── base.html      # Shared layout
│   │   ├── home.html      # Homepage
│   │   ├── auth/          # Auth templates
│   │   │   ├── login.html # Login page
│   │   │   ├── register.html # Register page
│   │   │   ├── reset_password.html # Password reset page
│   │   ├── main/          # Main templates
│   │   │   ├── dashboard.html # User dashboard
│   │   │   ├── index.html # Landing page
│   │   ├── profile/       # Profile templates
│   │   │   ├── profile.html # Enhanced profile form with tax fields
│   │   ├── budget/        # Budget templates
│   │   │   ├── name.html  # Budget name input
│   │   │   ├── budget_create.html # Budget category creation form
│   │   │   ├── budget_input.html  # Input form for budget details
│   │   │   ├── income.html # Income input form with tax type
│   │   │   ├── preview.html # Preview all budget data before calculation
│   │   │   ├── results.html # Final budget calculation results with tax details
│   │   │   ├── view_budget.html # View existing budget
│   ├── static/            # CSS and JavaScript
│   │   ├── css/           # Stylesheets
│   │   ├── js/           # JavaScript files
│   │   │   ├── budget_create.js # JS for budget creation
│   │   │   ├── income.js  # JS for income form handling
│   ├── config/            # Configuration settings
│   │   ├── __init__.py
│   │   ├── settings.py    # Flask settings (Development, Production, Testing)
├── migrations/            # Database migration files
│   ├── versions/         # Migration version files
│   │   ├── [migration_id]_add_tax_related_fields_to_profile_model.py
├── tests/                 # Unit and integration tests
│   ├── __init__.py
│   ├── test_routes.py     # API route tests
│   ├── test_models.py     # Model tests
│   ├── test_auth.py       # Auth tests
│   ├── test_budget.py     # Budget-specific tests
│   ├── test_tax_api.py    # Tests for tax rate API integration
│   ├── conftest.py        # Pytest configuration file (fixtures)
│   ├── mocks/             # Mock data for testing
│   │   ├── tax_api_responses.json # Mock responses for tax API
├── docs/                  # Project documentation
│   ├── structure_flask.md # Documentation for project structure
│   ├── api_documentation.md # Documentation for API usage
│   ├── tax_calculation.md # Documentation for tax calculation logic
├── .env                   # Environment variables (ignored in version control)
├── requirements.txt       # Python dependencies
├── run.py                 # Entry point to run the app
├── .gitignore             # Ignore unnecessary files
└── README.md              # Project documentation
