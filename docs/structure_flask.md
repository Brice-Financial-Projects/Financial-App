# Flask Application Structure

## Project Root Directory Structure
```
finance-budget-app/
├── app/                    # Main application package
├── archives/              # Archived code and files (old implementations, backups)
├── data/                  # Data files and resources (tax rates, state info)
├── docs/                  # Project documentation
│   ├── database_schema.md # Database models and relationships
│   ├── structure_flask.md # Project structure documentation
│   └── finance_budget_app_db_schema.png # Visual database schema
├── flask_session/        # Flask session storage files
├── migrations/           # Database migration files
│   ├── versions/        # Individual migration scripts
│   ├── env.py          # Migration environment settings
│   └── alembic.ini     # Alembic configuration
├── scripts/              # Utility and maintenance scripts
├── tests/               # Test suite
│   ├── __init__.py     # Test package initialization
│   ├── conftest.py     # Test fixtures and configuration
│   ├── functional/     # View and route testing
│   │   ├── __init__.py # Functional tests initialization
│   │   ├── test_auth_views.py    # Authentication view tests
│   │   ├── test_budget_views.py  # Budget view tests
│   │   ├── test_profile_views.py # Profile view tests
│   │   └── test_weather_views.py # Weather view tests
│   ├── integration/    # External system integration tests
│   │   ├── __init__.py # Integration tests initialization
│   │   ├── test_db.py  # Database integration tests
│   │   └── test_weather_api.py # Weather API integration tests
│   └── unit/          # Unit tests for models and utilities
│       ├── __init__.py # Unit tests initialization
│       ├── test_models.py # Database model tests
│       └── test_utils.py  # Utility function tests
├── venv/                 # Python virtual environment
├── .env                  # Environment variables and secrets
├── .gitignore           # Git ignore patterns
├── budget_app.log       # Application logging file
├── pytest.ini           # Pytest configuration and settings
├── README.md            # Project overview and setup instructions
├── requirements.txt     # Python package dependencies
├── run.py               # Application entry point
└── test_db.py          # Test database configuration
```

## Application Package Structure (app/)
```
app/
├── __init__.py          # Application factory, extensions, and blueprints
├── models.py            # SQLAlchemy models (User, Profile, Budget, etc.)
├── forms.py            # Common form definitions
├── utils.py            # Shared utility functions
├── api/                # API endpoints and integrations
│   ├── __init__.py    # API blueprint initialization
│   ├── routes.py      # API route definitions
│   └── services.py    # External service integrations
├── auth/               # Authentication blueprint
│   ├── __init__.py    # Blueprint initialization
│   ├── forms.py       # Login, registration, and password forms
│   ├── routes.py      # Auth routes (login, register, logout)
│   └── utils.py       # Auth-specific utilities
├── budget/             # Budget management blueprint
│   ├── __init__.py    # Blueprint initialization
│   ├── forms.py       # Budget creation and management forms
│   ├── routes.py      # Budget CRUD operations
│   ├── budget_logic.py # Budget calculations and business logic
│   └── utils.py       # Budget-specific utilities
├── config/             # Configuration settings
│   ├── __init__.py    # Config initialization
│   └── settings.py    # Environment-specific settings
├── debt/               # Debt management blueprint
│   ├── __init__.py    # Blueprint initialization
│   ├── forms.py       # Debt tracking forms
│   └── routes.py      # Debt management routes
├── main/              # Main application blueprint
│   ├── __init__.py    # Blueprint initialization
│   ├── routes.py      # Core routes (home, dashboard)
│   └── errors.py      # Error handlers
├── profile/           # Profile management blueprint
│   ├── __init__.py    # Blueprint initialization
│   ├── forms.py       # Profile forms with tax information
│   ├── routes.py      # Profile CRUD operations
│   └── utils.py       # Profile-specific utilities
├── static/            # Static files
│   ├── css/          # Stylesheets
│   │   ├── style.css # Main stylesheet
│   │   └── forms.css # Form-specific styles
│   ├── js/           # JavaScript files
│   │   ├── budget.js # Budget form handling
│   │   ├── income.js # Income calculations
│   │   └── utils.js  # Shared functions
│   └── img/          # Images and icons
├── templates/         # Jinja2 HTML templates
│   ├── auth/         # Authentication templates
│   │   ├── login.html    # Login form
│   │   ├── register.html # Registration form
│   │   └── reset.html    # Password reset
│   ├── budget/       # Budget templates
│   │   ├── create.html   # Budget creation
│   │   ├── view.html     # Budget display
│   │   ├── edit.html     # Budget modification
│   │   └── list.html     # Budget listing
│   ├── main/         # Core templates
│   │   ├── home.html     # Landing page
│   │   └── dashboard.html # User dashboard
│   ├── profile/      # Profile templates
│   │   ├── create.html   # Profile creation
│   │   └── edit.html     # Profile editing
│   ├── weather/      # Weather templates
│   │   └── weather.html  # Weather display
│   ├── base.html     # Base template with layout
│   ├── header.html   # Navigation header
│   └── footer.html   # Page footer
└── weather/          # Weather integration blueprint
    ├── __init__.py   # Blueprint initialization
    ├── forms.py      # Weather search forms
    ├── routes.py     # Weather routes
    └── service.py    # OpenWeather API integration
```