# Redis with the Deployment of Postgres in Render for Budget Sync

```graphql

                        ┌───────────────────────┐
                        │   BudgetSync Flask    │
                        │        App            │
                        └──────────┬────────────┘
                                   │
                                   │ Uses SQLAlchemy for queries
                                   ▼
                        ┌───────────────────────┐
                        │      Postgres DB      │
                        │  (Render Managed)     │
                        └──────────┬────────────┘
                                   │
                                   │ SQL queries, connection pooling
                                   ▼
                        ┌───────────────────────┐
                        │   Render Postgres      │
                        │  Environment URL       │
                        │ DATABASE_URL           │
                        └───────────────────────┘

                                   ▲
                                   │
                                   │ Flask-Session uses
                                   │ REDIS_URL string
                                   ▼
                        ┌───────────────────────┐
                        │        Redis          │
                        │  (Render Managed)     │
                        └──────────┬────────────┘
                                   │
                                   │ Stores session data
                                   │ Lazy connection by Flask-Session
                                   ▼
                        ┌───────────────────────┐
                        │ Session storage /     │
                        │ Authentication data   │
                        └───────────────────────┘
```

Notes:
- Flask app reads DATABASE_URL and REDIS_URL from environment variables.
- Flask-Session handles Redis connections internally; no manual Redis client needed in config.
- Postgres connection pooling handled by SQLAlchemy settings in ProductionConfig.
- This setup keeps app startup safe, scalable, and production-ready.