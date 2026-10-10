from redis import Redis

from django_ratelimiter.backends.memory import MemoryBackend
from django_ratelimiter.backends.redis import RedisBackend

from django.core.exceptions import ImproperlyConfigured




from functools import lru_cache

@lru_cache(maxsize=8)
def _redis_backend_for_url(redis_url):
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

