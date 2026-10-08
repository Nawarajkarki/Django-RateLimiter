
### _state dict format will be 
# {
#     "user_123" : {
#         "window_id" = 1223,
#         "request_count" = 12
#     },
#     "user_233" : {
#         "window_id" : 323,
#         "request_count" : 14
#     }


from threading import Lock

class MemoryBackend:
    def __init__(self):
        self._store = {}
        self._lock = Lock()     
        self._locks = {}

    def get(self, key):
        with self._lock:
            return self._store.get(key)

    def set(self, key, state):
        with self._lock:
            self._store[key] = state

    def lock(self, key):
        with self._lock:
            if key not in self._locks:
                self._locks[key] = Lock()

            return self._locks[key]