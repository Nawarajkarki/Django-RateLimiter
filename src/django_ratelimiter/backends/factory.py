from redis import Redis

from django_ratelimiter.backends.memory import MemoryBackend
from django_ratelimiter.backends.redis import RedisBackend

from django.core.exceptions import ImproperlyConfigured

def build_backend(config):
    
    backend_name = config['BACKEND'].lower()
    
    normalized_backend = backend_name.lower().strip()
    
    if normalized_backend == "memory":
        return MemoryBackend()
    
    if normalized_backend == "redis":
        client = Redis.from_url(config["REDIS_URL"], protocol=2)
        return RedisBackend(client)
    
    raise ImproperlyConfigured(
        f"Unsupported rate-limiter backend: {backend_name}"
    )
