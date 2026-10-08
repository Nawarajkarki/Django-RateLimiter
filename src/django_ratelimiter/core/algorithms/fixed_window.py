import math
from time import time



class FixedWindow:
    
    def __init__(self, limit, window_size, backend):
        
        if (
            isinstance(limit, bool)
            or isinstance(window_size, bool)
            or not isinstance(limit, int)
            or not isinstance(window_size, int)
        ):
            raise TypeError("limit and window_size must be integers")

        if limit <= 0 or window_size <= 0:
            raise ValueError("limit and window_size must be greater than zero")
        
        self.limit = limit
        self.window_size = window_size
        self.backend = backend
        
        
    def check(self, key):
        now = time()
        current_window = int(now // self.window_size)
        window_end = (current_window + 1) * self.window_size
        state = self.backend.get(key)
        

        
        
        if state is None:
            new_state = {
                "window_id" : current_window,
                "request_count" : 1
            }
            self.backend.set(key, new_state)
            
            return {"allowed" : True}
        
        if state['window_id'] != current_window:
            new_state = {
                "window_id" : current_window,
                "request_count" : 1
            }
            self.backend.set(key, new_state)
            
            return {"allowed" : True}
        
        if state['request_count'] >= self.limit:
            retry_after = math.ceil(window_end - now)
            return {"allowed" : False, "retry_after" : retry_after}

        state["request_count"] += 1
        self.backend.set(key, state)
        
        return {"allowed" : True}