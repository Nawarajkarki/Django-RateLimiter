import json

from redis.exceptions import WatchError

class RedisBackend:
    def __init__(self, client, key_prefix="django_ratelimiter"):
        self.client = client
        self.key_prefix = key_prefix.rstrip(":")
        
    def _redis_key(self, key):
        return f"{self.key_prefix}:{key}"
    
    def get(self, key):
        raw_state = self.client.get(self._redis_key(key))
        
        if raw_state is None:
            return None
        
        return json.loads(raw_state)

    def set(self, key, state, timeout = None):
        options = {}
        if timeout is not None:
            options["ex"] = timeout
            
        self.client.set(
            self._redis_key(key),
            json.dumps(state),
            **options,
        )
        
    def update(self, key, updater):
        redis_key = self._redis_key(key)
        while True:
            with self.client.pipeline() as pipe:
                try:
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
                    
                        