SECRET_KEY = "test-only"
INSTALLED_APPS = []
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

RATE_LIMITER = {
    "ALGORITHM": "fixed_window",
    "LIMIT": 10,
    "WINDOW_SECONDS": 60,
    "KEY_FUNCTION": "myproject.ratelimit.get_rate_limit_key",
    "BACKEND": "memory",  # "memory" or "redis"
}