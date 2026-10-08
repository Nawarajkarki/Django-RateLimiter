# Django Rate Limiter

## Django middleware configuration

Add the middleware and rate-limit settings to your Django project's `settings.py`:

```python
MIDDLEWARE = [
    # ...
    "django_ratelimiter.integrations.middleware.RateLimitMiddleware",
]

RATE_LIMITER = {
    "ALGORITHM": "fixed_window",
    "LIMIT": 10,
    "WINDOW_SECONDS": 60,
    "KEY_FUNCTION": "myproject.ratelimit.get_rate_limit_key",
}
```

- `ALGORITHM`: rate-limiting algorithm. Currently, only `fixed_window` is implemented.
- `LIMIT`: maximum allowed requests for one key in a window.
- `WINDOW_SECONDS`: window duration in seconds.
- `KEY_FUNCTION`: dotted Python path to a function that accepts a Django request and returns a stable key, such as `user:42` or `ip:203.0.113.10`. Requests returning the same key share a limit.

The current in-memory backend keeps counts within one process; separate worker processes do not share counters.
