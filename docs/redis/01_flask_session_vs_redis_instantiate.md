

```graphviz
                    ┌────────────────────┐
                    │      Flask App     │
                    └─────────┬──────────┘
                              │
            ┌─────────────────┴─────────────────┐
            │                                   │
            ▼                                   ▼
  Approach 1: Flask-Session URL          Approach 2: Manual Redis
           (Recommended)                     (Full Control)

   ┌───────────────────────────┐        ┌───────────────────────────┐
   │ SESSION_TYPE = "redis"    │        │ REDIS_URL = Redis.from_url│
   │ REDIS_URL = "redis://…"   │        │ ("redis://…")             │
   └─────────┬─────────────────┘        └─────────┬─────────────────┘
             │                                    │
             │ Flask-Session parses URL           │ Client created at config load
             │ and instantiates Redis client      │ (import time)
             ▼                                    ▼
       Redis client managed internally       Redis client must be managed
       Lazy connection on first session      manually for pooling, errors
             │                                    │
             │ Connection errors handled        │ Connection errors may crash
             │ lazily (retry/fallback)         │ app at startup
             ▼                                    ▼
      Sessions stored in Redis               Sessions stored in Redis
      automatically                            manually
```

## Takeaways from the diagram
1. Flask-Session URL approach (left)
  * Lazy connections, automatic error handling
  * Config remains simple, safe, and production-ready
  * Matches Flask-Session expectations, no .startswith errors

2. Manual Redis instantiation (right)
  * Gives you full control for caching, queues, etc.
  * Introduces startup fragility if Redis is unavailable
  * Must manually handle pooling, timeouts, and session integration