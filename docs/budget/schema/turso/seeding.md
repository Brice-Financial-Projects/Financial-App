# Database Seeding Guide (seed.py)

This project uses a hybrid database initialization strategy designed for Turso (SQLite):

- schema.sql → creates database tables (run once per database)
- seed.py → inserts initial application data (safe to re-run)

The seeding process is idempotent, environment-driven, and secure:

- No credentials are hardcoded
- No duplicate records are created
- The script can be safely re-run without data loss

---

## What seed.py Does

When executed, seed.py will:

- Create an admin user (if one does not already exist)
- Create an admin profile
- Seed base expense categories
- Seed default expense templates
- It will NOT overwrite existing records
- It will NOT delete data or reset passwords

This script is intended for:

- Local development
- Initial deployment
- Staging / test environments

---

## Prerequisites

Before running the seed script, ensure the following are complete:

1. The database exists in Turso
2. The database schema has been applied
3. Environment variables are configured
4. The application can connect to the database

---

## Step 1: Create the Database Schema

Apply the schema to your Turso database:

```bash
turso db shell <your-db-name> < schema.sql
```

Verify that tables were created successfully before proceeding.

---

## Step 2: Configure Environment Variables

Copy the example environment file:

cp .env.example .env

Populate at minimum the following variables in .env:

DATABASE_URL=libsql://your-db-name.turso.io  
TURSO_AUTH_TOKEN=your-turso-auth-token  

ADMIN_EMAIL=<admin@yourdomain.com>
ADMIN_USERNAME=admin  
ADMIN_PASSWORD=StrongPasswordChangeMe!  

Important notes:

- Never commit the .env file
- Rotate the admin password after first login
- .env.example should be committed; .env should not

---

## Step 3: Run the Seed Script

From the project root directory:

python seed.py

On success, you should see:

Database seeded successfully.

---

## What Happens If You Run It Again?

Nothing destructive.

The script:

- Checks for existing records before inserting
- Skips data that already exists
- Avoids creating duplicates

This makes it safe for:

- Redeployments
- CI environments
- Rebuilding local databases

---

## Admin Login After Seeding

After the seed completes, you can log in using:

Email: value of ADMIN_EMAIL  
Password: value of ADMIN_PASSWORD  

It is strongly recommended to:

- Change the admin password immediately
- Rotate or remove seed credentials in production

---

## Common Errors and Troubleshooting

### Missing environment variables

Error:
ADMIN_EMAIL and ADMIN_PASSWORD must be set

Fix:
Ensure .env exists and all required variables are populated.

---

### Database connection issues

Fix:

- Verify DATABASE_URL
- Verify TURSO_AUTH_TOKEN
- Confirm the schema was applied successfully

---

## Security Considerations

- seed.py never stores plaintext passwords
- Passwords are hashed using bcrypt before persistence
- Credentials are loaded from environment variables only
- The seed script itself is safe to commit to GitHub

---

## When NOT to Use seed.py

Do not use this script for:

- Production user creation
- Password resets
- Database migrations

It is intended solely for initial database bootstrapping.

---

## Summary

- schema.sql → database structure
- seed.py → initial data
- .env → secrets (never committed)
- .env.example → configuration documentation

This approach keeps the system secure, reproducible, easy to deploy, and easy to review.
