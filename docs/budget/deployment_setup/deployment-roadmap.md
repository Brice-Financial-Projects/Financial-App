<!--docs/budget/deployment_setup/deployment-roadmap.md-->

# Budget Application – Deployment Preparation and Feature Enhancement Roadmap

This document outlines the next development phases for preparing the budget application for production deployment. The current functionality demonstrates core backend proficiency and a user-focused design. The following phases are structured to enhance security, improve deployment readiness, and ensure the application meets professional standards expected in production environments.

---

## Current Functionality Overview

- User registration with enforced password complexity (uppercase, lowercase, number, special character, and minimum length)
- Authentication system with login flow and flash-based feedback
- Profile completion requirement prior to budget creation
- Support for multiple budget records per user
- Monthly budget calculation based on income frequency selection
- Weather API integration accessible via user dashboard
- Local PostgreSQL database with structured persistence logic

---

## Phase 1 – Password Reset Implementation

**Objective:** Implement a secure and user-friendly password reset flow.

**Tasks:**
- Add “Forgot Password?” link to the login interface
- Generate secure, time-limited tokens using JWT or `itsdangerous`
- Integrate email functionality using a service such as SendGrid
- Develop reset confirmation forms and handling routes
- Implement appropriate success and error flash messaging

**Rationale:**  
Enables recovery of user credentials and aligns the application with standard authentication practices.

---

## Phase 2 – Deployment Branch and Environment Configuration

**Objective:** Prepare for staging and production deployments using modern hosting and database services.

**Tasks:**
- Create a dedicated deployment branch  
  ```bash
  git checkout -b deployment-setup
  ```
- Select deployment strategy:
  - **Heroku:** Host the application and manage environment variables
  - **Supabase:** Replace local PostgreSQL with cloud-managed database
- Configure `.env` files and production-safe defaults

**Rationale:**  
Facilitates deployment to cloud platforms and prepares for future scalability.

---

## Phase 3 – Security Enhancements

**Objective:** Harden the application against common vulnerabilities and ensure secure deployment.

**Tasks:**
- Confirm use of `bcrypt` for password hashing
- Enforce CSRF protection via Flask-WTF
- Apply thorough input validation on all forms and API endpoints
- Add secure HTTP headers using Flask-Talisman
- Redirect all traffic to HTTPS in production environments

**Rationale:**  
Ensures the application meets modern backend security expectations and best practices.

---

## Phase 4 – Docker Containerization (Optional)

**Objective:** Introduce containerization to standardize development and deployment environments.

**Tasks:**
- Write a `Dockerfile` to containerize the Flask application
- Optionally configure `docker-compose.yml` to include:
  - Flask application service
  - PostgreSQL service (or external Supabase integration)

**Rationale:**  
Containerization supports reproducible builds and simplifies team-based or cloud deployments.

---

## Phase 5 – Documentation and Presentation

**Objective:** Finalize all documentation and prepare the application for professional demonstration or hiring use cases.

**Tasks:**
- Update the `README.md` to include:
  - Overview of the application and its purpose
  - Features and architecture summary
  - Setup instructions for local and cloud deployment
  - Screenshots or embedded GIFs showing core functionality
  - Security considerations and implementation notes
- (Optional) Author a blog post on building a secure budgeting platform using Flask and modern backend tools

**Rationale:**  
Clear documentation increases project credibility and aids technical reviewers in quickly evaluating design and functionality.

---

## Summary Checklist

| Priority     | Task                                                                 |
|--------------|----------------------------------------------------------------------|
| High         | Implement password reset functionality via SendGrid + secure tokens |
| High         | Establish deployment branch and configure Supabase or Heroku        |
| Medium       | Perform security hardening (CSRF, HTTPS, input validation, headers) |
| Medium       | Add Docker support for development and deployment                   |
| Continuous   | Maintain and polish documentation and public-facing assets          |

---

## Conclusion

Upon completion of the above phases, the budget application will be positioned for professional-grade deployment and demonstration. The roadmap emphasizes security, deployment realism, and backend reliability—making it suitable for inclusion in a backend engineering portfolio or as a technical artifact for prospective employers.
