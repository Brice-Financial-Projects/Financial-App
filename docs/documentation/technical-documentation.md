# 🧾 BudgetSync Internal Technical Documentation

## Overview

**BudgetSync** is a Flask-based budgeting application developed as a capstone project. It allows users to manage income, track expenses, and simulate tax withholding. The project emphasizes secure authentication, modular budgeting, and simple data integration. To meet the capstone’s API requirement, a weather API was added to the dashboard. A full-featured tax API was planned but is currently archived; instead, a generic placeholder tax calculation is used for now.

---

## 1. Application Architecture

- **Flask**: Web framework
- **PostgreSQL**: Primary data store
- **SQLAlchemy**: ORM layer
- **Redis**: Session management
- **SendGrid**: Email delivery (password reset)
- **OpenWeatherMap**: Weather integration
- **itsdangerous**: Token generation for password reset
- **Flask-Login** / **Flask-Session** / **Flask-Bcrypt**: Core auth stack

---

## 2. Feature Summary

### ✅ Core Features Implemented
- Secure user registration and login
- Profile management (tax info, benefits, employment)
- Budget creation and editing
- Income frequency normalization
- Expense categorization (min/preferred payments)
- Basic tax withholding estimation (non-API)
- Weather API integration (external)
- Flash messaging and validation

### 🚧 In Progress or Needs Improvement
- Budget preview and navigation flow
- Tax summary logic on budget pages
- Edit budget from dashboard
- Transitions between input stages
- Inline help/tooltips
- Visualization components (e.g., tax burden chart)

---

## 3. Authentication & Session Management

- Passwords hashed using **Flask-Bcrypt**
- Sessions managed using **Flask-Session** backed by Redis
- Login handled with **Flask-Login**
- All protected routes redirect unauthorized users to login
- Password reset flow uses `itsdangerous` for secure token generation and SendGrid for email delivery
- User profile completion is mandatory before creating a budget

---

## 4. Tax Calculation Logic (Generic, Not API-Driven)

### Background:
Originally, the plan was to implement a custom tax API with proper endpoints and dynamic logic. However, due to time constraints, the tax API was archived. A **non-realistic, generic tax calculation module** was developed to simulate withholding and support budgeting logic.

### Current Implementation:
- Purely internal; not exposed via API
- No actual tax bracket logic — fixed calculations only
- Accepts basic profile inputs (e.g., income, dependents, withholdings)

### Behavior:
- Runs behind the scenes when calculating a budget
- Does not reflect accurate IRS, FICA, or state-level tax rules
- No real projection or withholding tables

### Future Direction:
- Replace with dynamic internal module or connect to public tax datasets
- Include tax visualization and breakdown (planned)

---

## 5. Weather API Integration (External API)

### Purpose:
To fulfill the bootcamp’s requirement for an API integration, the OpenWeatherMap API was added to the dashboard. This replaced an abandoned plan to develop a custom tax API due to time constraints.

### Route:
POST /weather/weather

### Parameters:
- city: City name (e.g., "Tampa")
- state: Two-letter U.S. state abbreviation (e.g., "FL")
- country: Country code (e.g., "US")

### Output:
- JSON response includes:
  - Temperature
  - Weather condition (e.g., "Cloudy", "Sunny")
  - Humidity
  - Wind speed

### Notes:
- API key must be set as `OPENWEATHER_API_KEY` in `.env`
- Integration is read-only (weather data is not stored)
- No retry, fallback, or caching logic implemented
- Minimal user feedback on API failure (future improvement needed)

---

## 6. Budget Creation Workflow

### Step-by-Step:
1. User Registration & Login
2. Complete Profile: Includes income type, frequency, deductions, etc.
3. Create Budget from dashboard
4. Input Income Sources: Each with its own frequency (weekly, monthly, etc.)
5. Normalize Income to monthly values
6. Input Expense Items: Includes min/preferred payments
7. Apply Basic Tax Estimate (generic logic)
8. Store Budget in database with status `draft` or `final`

---

## 7. Income Normalization Logic

| Frequency | Formula Used     |
|-----------|------------------|
| Weekly    | amount ÷ 52      |
| Biweekly  | amount ÷ 26 x 2  |
| Monthly   | amount ÷ 12          |

- Gross annual income is collected as input from the user.
- Normalized monthly income is summed from all sources.
- Tax estimate and deductions are applied to this figure to simulate net income.

---

## 8. Flash Messaging System

### Categories Used:
- `success`: Positive confirmation (e.g., "Budget created")
- `error`: Validation or system error
- `info`: Guidance messages

### Status:
- Flash messages now rendered globally via `base.html`
- Minor bug fixed where messages were delayed
- Still needs improved wording and conditional logic

---

## 9. Outstanding Bugs and Backlog (as of April 2025)

| Area             | Description                                            |Status
|------------------|--------------------------------------------------------|------------------|
| Budget Routing   | Budget creation skips category selection page          |Category selection page added |
| Budget Edit      | Edit form does not pre-fill or retain changes          |Edit form works as intended |
| Preview Budget   | Does not render calculated budget summary              |Calculation logic updated to render proper numbers |
| Flash UX         | Messages sometimes inaccurate or redundant             |Messaging was in the wrong location.  Been updated to the appropriate template location in the base file. |
| Weather API      | No fallback or graceful error handling                 |
| Generic Tax Logic| Not connected to all relevant profile fields           |

---

## 10. Planned Enhancements

- Add tax visualization to budget preview
- Support state-specific tax rules
- Introduce debt payoff planner (snowball method)
- Export annual budget summary to PDF
- Add mobile-responsive views
- Add admin dashboard for managing users and budgets
- Integrate caching for API responses

---

## 11. Archived Tax API (Background)

- The original intent was to build a fully functional internal tax API.
- This was shelved due to project time constraints.
- Codebase exists in an `/archive/` directory with partial logic and endpoints.
- It may be developed post-capstone for real tax forecasting and comparison.

---

## 12. Environment Configuration

`.env` file must include:
- `FLASK_ENV=development`
- `FLASK_DEBUG=1`
- `SECRET_KEY=your_secret_key`
- `DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/dbname`
- `REDIS_URL=redis://localhost:6379/0`
- `OPENWEATHER_API_KEY=your_api_key`
- `SENDGRID_API_KEY=your_sendgrid_api_key`

---

## 13. Testing and Debugging

### Current Status:
- Manual testing performed for major flows
- No automated tests implemented yet

### Testing Goals:
- Unit tests for income normalization and budget logic
- Flash message testing
- Simulated API failure handling for weather requests
- Password reset and session timeout tests

---

## 14. Project Conclusion

**BudgetSync** is a functional capstone-level financial planning tool. It demonstrates core backend engineering principles including authentication, budgeting logic, ORM modeling, and API integration.

The current system lays the groundwork for future expansion, including:
- Real tax computation
- Debt management
- Secure production deployment
- Scalable architecture for professional use

This concludes the internal documentation from Section 5 to Section 14.
