# Project File Structure With Frontend

flask_budget_app/
├── backend/                  # Flask backend (API-only)
│   ├── app/                  # Main Flask application
│   │   ├── __init__.py       # Initialize Flask app and extensions
│   │   ├── models.py         # General SQLAlchemy models (shared across app)
│   │   ├── forms.py          # General WTForms for shared functionality
│   │   ├── templates/        # Flask templates (for admin or API testing only)
│   │   │   └── base.html     # General HTML base template for Flask views
│   │   ├── static/           # Shared static files (CSS, JS, images) if needed
|   |   ├── auth/             # Auth-specific functionality
|   |   │   ├── __init__.py   # Init file for the auth module
|   |   │   ├── routes.py     # Auth-specific routes
|   |   │   ├── forms.py      # Auth-specific forms
|   |   │   └── models.py     # Auth-specific models
|   |   ├── main/             # General module
|   |   │   ├── __init__.py   # Init file for the main module
|   |   │   └── routes.py     # Main routes
│   │   ├── budget/           # Budget-specific functionality
│   │   │   ├── __init__.py   # Init file for the budget module
│   │   │   ├── routes.py     # Budget-specific routes
│   │   │   ├── utils.py      # Budget-specific utility functions
│   │   │   ├── models.py     # Budget-specific models
│   │   │   └── templates/    # Budget-specific templates
│   │   │       ├── form.html # Budget input form (optional for server-side)
│   │   │       └── dashboard.html # Budget dashboard view (optional for server-side)
│   │   ├── debt/             # Debt-specific functionality
│   │   │   ├── __init__.py   # Init file for the debt module
│   │   │   ├── routes.py     # Debt-specific routes
│   │   │   ├── utils.py      # Debt-specific utility functions
│   │   │   ├── models.py     # Debt-specific models
│   │   │   └── templates/    # Debt-specific templates (later development)
│   │           ├── payoff.html # Debt payoff strategies view (later)
│   │           └── overview.html # Debt overview view (later)
│   ├── migrations/           # Alembic migration files
│   ├── tests/                # Unit tests for the backend
│   ├── .env                  # Environment variables for Flask
│   ├── requirements.txt      # Python dependencies
│   ├── run.py                # Entry point for running Flask
│   └── README.md             # Backend-specific documentation
│
├── frontend/                  # React or Next.js frontend
│   ├── public/               # Static assets (e.g., images, fonts)
│   ├── src/                  # Source code
│   │   ├── components/       # Reusable React components
│   │   │   ├── Navbar.js     # Navigation bar (e.g., dashboard options)
│   │   │   ├── Dashboard.js  # Main dashboard component
│   │   │   ├── BudgetForm.js # Budget form component
│   │   │   └── DebtPayoff.js # Placeholder for debt payoff feature
│   │   ├── pages/            # Pages for Next.js (or React routing)
│   │   │   ├── index.js      # Home/dashboard page
│   │   │   ├── budget.js     # Budget page
│   │   │   └── debt.js       # Debt payoff page (later development)
│   │   ├── styles/           # CSS/SCSS files
│   │   │   ├── dashboard.css # Dashboard-specific styles
│   │   │   └── forms.css     # Form styles
│   │   ├── utils/            # Utility functions (e.g., API calls)
│   │   │   └── api.js        # API service for connecting to Flask backend
│   ├── .env.local            # Frontend-specific environment variables
│   ├── package.json          # Frontend dependencies and scripts
│   └── README.md             # Frontend-specific documentation
│
├── .gitignore                # Ignore unnecessary files for Git
├── README.md                 # Overall project documentation
└── docker-compose.yml        # Docker Compose file for combined setup
