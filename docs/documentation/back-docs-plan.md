<!--docs/documentation/bad-docs-plan.md-->

# 📚 BudgetSync Back-Documentation Plan

## 1. High-Level Docs

### `README.md`
- Project summary
- Key features:
  - User authentication
  - Budget creation with income frequency conversion
  - Weather API integration on dashboard
  - User profile gating logic
- Tech stack (Flask, SQLAlchemy, Redis, SendGrid, etc.)
- Getting started (basic setup and .env configuration overview)
- Optional: UI screenshots

### `docs/overview.md`
- Project motivation and problem being solved
- User journey / flow
- Application architecture diagram (Flask + Redis + PostgreSQL + SendGrid)

---

## 2. Environment & Deployment

### `docs/setup.md`
- Local development setup instructions
- Required environment variables:
  - `SECRET_KEY`
  - `SENDGRID_API_KEY`
  - `REDIS_URL`
  - `DATABASE_URL`
- Redis setup for development and production
- Optional: Using a `.env.example` template

### `docs/deployment.md`
- Production deployment checklist
- Steps for Heroku (or other platform) deployment
- Gunicorn + Procfile setup (if used)
- Rate limiting and session storage via Redis
- Environment safety best practices (e.g., don't expose keys)

---

## 3. Security & Authentication

### `docs/security.md`
- Authentication flow (register → login → session)
- Flask-Login + Flask-Session setup
- Password hashing via Flask-Bcrypt
- Password policy enforcement
- Password reset token logic:
  - Uses `itsdangerous` for secure token generation
  - SendGrid for email delivery
- Rate limiting approach (Redis-based)

---

## 4. Features & Core Logic

### `docs/features/budgets.md`
- Income frequency handling (weekly, biweekly → monthly logic)
- Budget creation flow
- Monthly normalization explanation

### `docs/features/dashboard.md`
- Weather API integration
  - API used (e.g., OpenWeatherMap)
  - Rate limits and error fallback
- Dashboard logic overview

### `docs/features/profile.md`
- User profile gating logic:
  - Users must complete profile before creating a budget
  - Flash messaging and validation logic

---

## 5. Future Roadmap (Optional)

- Add admin panel and user management
- Analytics or reports dashboard
- Shared/family budgets
- Stripe integration for premium financial tools
- Mobile-friendly version


========================================================

# Back Documentation

========================================================

# 🔁 Back-Documentation Additions to Create

## 1. `docs/features/weather_api.md`
- Why it was added (to showcase external API integration)
- How the integration works (route → OpenWeather API → result rendering)
- Rate limit considerations
- Example API call

## 2. `docs/features/tax_api.md`
- Internal tax API endpoints
- Example JSON payloads (already present in `documentation.md`)
- Breakdown of calculation logic
- Future enhancements: state-specific logic, tax optimization

## 3. `docs/logic/income_normalization.md`
- Conversion logic for income frequency → monthly
- Use in budget totals
- Form validation

## 4. `docs/logic/profile_validation.md`
- Profile completion gating logic
- Required fields and why they matter
- Flash messaging behavior


=========================================================

# Detailed Plan

=========================================================

# 📚 Comprehensive Back-Documentation Plan for BudgetSync

This plan covers full internal and external documentation to reverse-document the application after development. All files are written in Markdown and organized by category and purpose.

---

## 🧭 1. Overview & Executive Documentation

### `README.md` (Public-Facing)
- What the app does (brief)
- Key features
- Tech stack
- Setup instructions
- Example usage
- License & contribution info

### `docs/overview.md` (Internal)
- Project motivation and problem statement
- Intended user personas (e.g., young professionals, families)
- High-level system diagram
- Feature prioritization rationale (e.g., why weather API was added instead of tax APIs)

---

## 🧪 2. Development and Runtime Environment

### `docs/setup/local_dev.md`
- Environment setup:
  - Python/Flask
  - PostgreSQL
  - Redis (local config with Docker or standalone)
- `.env` variable breakdown:
  - `SECRET_KEY`
  - `DATABASE_URL`
  - `REDIS_URL`
  - `SENDGRID_API_KEY`
  - `OPENWEATHER_API_KEY`

### `docs/deployment/production.md`
- Gunicorn and WSGI setup
- Redis in production (e.g., Heroku Redis or managed service)
- Session storage setup
- Security considerations for keys
- Debug mode vs production mode
- SendGrid DNS / domain considerations (from email settings)

---

## 🔐 3. Authentication & Authorization

### `docs/features/auth_flow.md`
- Registration logic (form, hashing with Flask-Bcrypt)
- Login logic (Flask-Login session mgmt)
- Flask-Session with Redis for production-safe sessions
- Profile gating:
  - Users must complete profile before creating budgets
  - Flash message behavior
- Password reset flow:
  - Token via `itsdangerous`
  - Email delivery via SendGrid
  - Reset URL generation using `request.host_url` (explain local vs prod)

---

## 💰 4. Budget Engine Logic

### `docs/features/budget_creation.md`
- Budget object lifecycle:
  - `draft` status
  - Linked to user and profile
- Form input validations
- Expense category structure
  - Minimum vs preferred payments
- Budget preview logic

### `docs/features/income_normalization.md`
- Frequencies supported (weekly, biweekly, monthly, annual)
- Monthly normalization logic
  - Formulas used (e.g., `weekly × 52 / 12`)
- Where normalized values are stored/used
- OtherIncome vs GrossIncome distinctions

---

## ☁️ 5. External Integrations

### `docs/features/weather_api.md`
- Why weather API was included (capstone requirement, tax APIs unavailable)
- Integration route
  - `POST /weather/weather`
- Parameters:
  - city, state, country
- Error handling (API fail, invalid city, etc.)
- OpenWeather API quota awareness
- Optional: add caching later

### `docs/features/tax_api.md`
- Internal endpoints:
  - `GET /api/v1/tax/federal/<year>`
  - `GET /api/v1/tax/state/<state>/<year>`
  - `POST /api/v1/tax/calculate`
- Example request/response JSON
- What’s implemented vs what’s stubbed
- Caching & auth plans for sensitive data

---

## 🗄️ 6. Database & Models

### `docs/database/models.md`
- Summary of each model (`User`, `Profile`, `Budget`, `BudgetItem`, etc.)
- Key fields and their purposes
- Relationships (ER diagram — you already have this in `database_schema.md`)

### `docs/database/migrations.md`
- How to manage schema changes
- Alembic migration commands
- Sample migration walk-through

---

## 🧪 7. Testing Plan

### `docs/testing/coverage.md`
- What’s been tested vs not
- Manual test checklist
- Future unit tests to add:
  - Tax API
  - Budget calculations
  - Profile validation logic
- Test framework used (`pytest`)

---

## 📈 8. Future Roadmap (Optional)

### `docs/roadmap.md`
- Planned improvements:
  - Tax optimization engine
  - Debt payoff visualizer
  - Admin dashboard
  - Mobile optimization
  - AI-driven suggestions
- Feature backlog with priorities

---

## 🛠️ Tools Used for Documentation (Optional)

If you want to generate diagrams:

- **Mermaid** (for ER, flow diagrams)
- **dbdiagram.io** (for visualizing schema from SQL or ORM)
- **Quarto or MkDocs** (if you publish docs)

---

## ✅ Immediate Next Steps

1. Copy this plan into a `docs/_README_BACKDOC_PLAN.md` file.
2. Choose one section (e.g., `auth_flow.md`) and backfill based on your current codebase.
3. Gradually fill each doc as you refactor or finalize production deployment.

