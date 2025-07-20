# 📋 Additional Questions:
1. Rate Limiting Storage: Should I use Redis for rate limiting (if available) or fall back to in-memory storage?
**Response: Redis**

2. Email From Address: What should be the "from" email address? (e.g., noreply@yourapp.com)


3. App Name: What should I use as the app name in the email template? (e.g., "Finance Budget App") 
**Response: Budget Sync**

4. Base URL: Should I use request.host_url to generate the reset link, or do you have a specific domain?



# 📋 Additional Design Decisions for Password Reset

| Question | Decision |
|---------|----------|
| **Rate Limiting Storage** | ✅ Use Redis for persistent, scalable rate-limiting |
| **Email From Address** | ✅ Use `brice@devbybrice.com` for SendGrid auth, display as `Budget Sync Support <donotreply@devbybrice.com>` |
| **App Name in Emails** | ✅ Use **Budget Sync** consistently in subject lines and body |
| **Base URL for Reset Link** | ✅ Use `APP_BASE_URL` from `.env` in production; fallback to `request.host_url` in dev |

