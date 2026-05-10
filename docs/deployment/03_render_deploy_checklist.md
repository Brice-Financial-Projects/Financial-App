# BudgetSync Render Deployment – Step-by-Step Checklist

---

## Step 0: Prep Your App

1. Make sure your Flask app runs locally with your current `config.py` / `.env` variables.  
2. Ensure your app uses environment variables for DB and Redis, not hardcoded values:

```
import os
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
```

3. Flask-Session config (for Redis):

```
from redis import Redis

SESSION_TYPE = "redis"
SESSION_REDIS = Redis.from_url(os.getenv("REDIS_URL"))
```

---

## Step 1: Create Postgres on Render

1. Go to Render Dashboard → New → Database → PostgreSQL  
2. Fill in:
   - Name: budget-db-instance (internal reference)  
   - Database Name: budget_db  
   - User: budget_user  
   - Password: auto-generated or strong password  
   - Region: match your app’s planned region  
   - Postgres Version: latest stable  
3. Click Deploy  
4. Copy the connection string Render provides. Example:

```
postgresql://budget_user:STRONG_PASSWORD@render-db-host:5432/budget_db
```

5. Test locally if desired:

```
psql postgresql://budget_user:STRONG_PASSWORD@render-db-host:5432/budget_db
```

---

## Step 2: Create Redis on Render

1. Go to Render Dashboard → New → Redis  
2. Fill in:
   - Name: budget-redis  
   - Region: same as Postgres  
3. Deploy and copy the connection URL Render gives you:

```
redis://:STRONG_PASSWORD@redis-host:6379/0
```

4. Test locally (optional):

```
import redis

r = redis.from_url("redis://:STRONG_PASSWORD@redis-host:6379/0")
r.set("test", "ok")
print(r.get("test"))  # should print b'ok'
```

---

## Step 3: Configure Environment Variables in Render

1. Open your Web Service in Render (BudgetSync app)  
2. Go to Environment → Environment Variables  
3. Add:

```
DATABASE_URL=postgresql://budget_user:STRONG_PASSWORD@render-db-host:5432/budget_db
REDIS_URL=redis://:STRONG_PASSWORD@redis-host:6379/0
FLASK_ENV=production
SECRET_KEY=<strong random string>
```

---

## Step 4: Local Verification Before Deploy

1. Update your local `.env` to match the Render URLs  
2. Run the app locally:

```
flask run
```

3. Verify:
   - Database connection works  
   - Redis sessions work (login/logout)  
   - App doesn’t crash  

4. Fix any errors now, before touching Docker or Render deploy

---

## Step 5: Optional Docker Prep (for practice)

1. Create a Dockerfile:

```
FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install --upgrade pip && pip install uv

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

CMD ["uv", "sync", "--frozen"]
```

2. Build and run locally:

```
docker build -t budgetsync .
docker run -p 5000:5000 --env-file .env budgetsync
```

---

## Step 6: Deploy App to Render

1. In Render, create Web Service → Connect to GitHub Repo  
2. Set Build Command:

```
curl -LsSf https://astral.sh/uv/install.sh | sh && source $HOME/.cargo/env && uv sync --frozen
```

3. Set Start Command (example):

```
gunicorn "budget_sync:create_app()"
```

4. Deploy and monitor logs  
5. Test all endpoints: login, budget creation, dashboard, etc.

---

### Why this workflow is “first-time-right”

- Postgres + Redis verified before deploy → deterministic debugging  
- App uses least privilege DB user → safe habit  
- Docker optional, but lets you practice containerization without breaking MVP  
- Environment variables hold secrets → production hygiene  
- App logs and failures are predictable, not a cascade of unknowns