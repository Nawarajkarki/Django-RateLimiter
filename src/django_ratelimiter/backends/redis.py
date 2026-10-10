import json

from redis.exceptions import RedisError, WatchError

from django_ratelimiter.exceptions import RateLimiterBackendError

class RedisBackend:
    def __init__(self, client, key_prefix="django_ratelimiter"):
        self.client = client
        self.key_prefix = key_prefix.rstrip(":")
        
    def _redis_key(self, key):
        return f"{self.key_prefix}:{key}"
    
    def get(self, key):
        try:
            raw_state = self.client.get(self._redis_key(key))
        except RedisError as exc:
            raise RateLimiterBackendError("Redis operation failed.") from exc
                
        if raw_state is None:
            return None
        
        return json.loads(raw_state)

    def set(self, key, state, timeout = None):
        options = {}
        if timeout is not None:
            options["ex"] = timeout
        
        try:
            self.client.set(
                self._redis_key(key),
                json.dumps(state),
                **options,
            )
        except RedisError as exc:
            raise RateLimiterBackendError("Redis operation failed.") from exc
        
        
    def update(self, key, updater):
        redis_key = self._redis_key(key)
        while True:
            try:
                with self.client.pipeline() as pipe:
                    pipe.watch(redis_key)
                    
                    raw_state = pipe.get(redis_key)
                    state = None if raw_state is None else json.loads(raw_state)
                    
                    new_state, result, timeout = updater(state)
                    
                    if new_state is None:
                        pipe.unwatch()
                        return result
                    
                    pipe.multi()
                    
                    options = {}
                    
                    if timeout is not None:
                        options["ex"] = timeout
                    
                    pipe.set(redis_key, json.dumps(new_state), **options)
                    pipe.execute()
                    
                    return result
                
            except WatchError:
                continue
            
            except RedisError as exc:
                raise RateLimiterBackendError("Redis operation failed.") from exc
                        