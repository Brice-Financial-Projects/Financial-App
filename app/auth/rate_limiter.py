"""Rate limiting utility for password reset requests."""

import time
from flask import current_app
from redis import Redis


class RateLimiter:
    """Rate limiter for password reset requests."""
    
    def __init__(self):
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = Redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            current_app.logger.warning(f"Redis not available for rate limiting: {e}")
            self.redis_client = None
    
    def is_rate_limited(self, email, max_requests=3, window_hours=1):
        """Check if email is rate limited for password reset requests."""
        if not self.redis_client:
            return False  # No rate limiting if Redis unavailable
        
        key = f"password_reset:{email}"
        window_seconds = window_hours * 3600
        
        try:
            # Get current count
            current_count = self.redis_client.get(key)
            current_count = int(current_count) if current_count else 0
            
            if current_count >= max_requests:
                return True
            
            # Increment count
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            pipe.execute()
            
            return False
        except Exception as e:
            current_app.logger.error(f"Rate limiting error: {e}")
            return False  # Allow request if rate limiting fails
    
    def get_remaining_time(self, email, window_hours=1):
        """Get remaining time until rate limit resets."""
        if not self.redis_client:
            return 0
        
        key = f"password_reset:{email}"
        try:
            ttl = self.redis_client.ttl(key)
            return max(0, ttl)
        except:
            return 0


# Global rate limiter instance
rate_limiter = RateLimiter() 