
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


class MemoryBackend:
    
    def __init__(self):
        self._store = {}
    
    def get(self, key):
        return self._store.get(key)
    
    
    def set(self, key, state) :
        self._store[key] = state
        