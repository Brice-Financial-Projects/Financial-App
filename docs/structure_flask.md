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
├── tests/                # Test files and configurations
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
├── tests/            # Test suite
│   ├── conftest.py   # Test fixtures and configuration
│   ├── test_auth.py  # Authentication tests
│   ├── test_budget.py # Budget functionality tests
│   ├── test_profile.py # Profile management tests
│   └── test_weather.py # Weather integration tests
└── weather/          # Weather integration blueprint
    ├── __init__.py   # Blueprint initialization
    ├── forms.py      # Weather search forms
    ├── routes.py     # Weather routes
    └── service.py    # OpenWeather API integration
```

## Key Components

### Configuration
- `config/settings.py`: Environment-specific configurations
  - Development settings with debug features
  - Production settings with security measures
  - Testing settings for automated tests
- `.env`: Environment variables
  - Database URLs
  - API keys and secrets
  - Flask configuration
- `pytest.ini`: Testing configuration
  - Test discovery rules
  - Plugin settings
  - Test markers

### Database
- `models.py`: SQLAlchemy models
  - User model with authentication
  - Profile model with tax information
  - Budget model with relationships
  - Income and expense tracking
- `migrations/`: Alembic migration files
  - Version-controlled schema changes
  - Data migrations
  - Rollback capabilities

### Routes and Views
Each blueprint contains:
- `routes.py`: Route definitions and view logic
- `forms.py`: WTForms for data validation
- `utils.py`: Blueprint-specific helper functions
- Custom business logic (e.g., `budget_logic.py`)

### Templates
Organized by blueprint with shared layouts:
- `base.html`: Base template with common structure
- Blueprint-specific template folders
- Partial templates for reusable components
- Consistent styling and navigation

### Static Files
- `static/css/`: Stylesheets
  - Main application styles
  - Blueprint-specific styles
  - Third-party CSS
- `static/js/`: JavaScript files
  - Form handling and validation
  - AJAX requests
  - UI interactions
- `static/img/`: Images and icons
  - Application assets
  - User uploads
  - UI elements

### Testing
- `tests/`: Test files organized by component
  - Unit tests for models and utilities
  - Integration tests for routes
  - Functional tests for features
- `conftest.py`: Shared test fixtures
  - Database setup
  - Authentication helpers
  - Mock objects

### Documentation
- `docs/`: Project documentation
  - `database_schema.md`: Database documentation
  - `structure_flask.md`: Project structure
  - API documentation
  - Setup and deployment guides

## Notes
- Each blueprint is self-contained with its own routes, forms, and templates
- Configuration is environment-aware (development, testing, production)
- Tests are organized by component for maintainability
- Static files and templates follow blueprint organization
- Documentation is maintained in Markdown format
- Consistent naming conventions across the project
- Modular design for easy feature additions
- Comprehensive error handling and logging
- Security best practices implemented throughout
