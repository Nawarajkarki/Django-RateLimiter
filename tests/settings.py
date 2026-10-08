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
    "LIMIT": 1,
    "WINDOW_SECONDS": 60,
    "KEY_FUNCTION": "unused.in.test",
}