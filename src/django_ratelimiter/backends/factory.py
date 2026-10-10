from functools import lru_cache

from django.core.exceptions import ImproperlyConfigured
from django_ratelimiter.backends.memory import MemoryBackend


@lru_cache(maxsize=8)
def _redis_backend_for_url(redis_url):
    try:
        from redis import Redis
        from django_ratelimiter.backends.redis import RedisBackend
    except ImportError as exc:
        raise ImproperlyConfigured(
            "The Redis backend requires the 'redis' extra. "
            "Install django-ratelimiter with Redis support."
        ) from exc

    client = Redis.from_url(redis_url, protocol=2)
    return RedisBackend(client)



def build_backend(config):
    normalized_backend = config['BACKEND'].strip().lower()
    
    if normalized_backend == "memory":
        return MemoryBackend()
    
    if normalized_backend == "redis":
        return _redis_backend_for_url(config["REDIS_URL"])
    
    raise ImproperlyConfigured(
        f"Unsupported rate-limiter backend: {normalized_backend}"
    )

