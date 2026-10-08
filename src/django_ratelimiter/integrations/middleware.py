from django.conf import settings
from django.http import HttpResponse
from django.utils.module_loading import import_string

from django_ratelimiter.backends.memory import MemoryBackend
from django_ratelimiter.core.algorithms.fixed_window import FixedWindow
from django_ratelimiter.core.limiter import build_limiter



class RateLimitMiddleware:
    
    def __init__(self, get_response):
        self. get_response = get_response
        
        backend = MemoryBackend()
        config = settings.RATE_LIMITER
        key_function = import_string(config["KEY_FUNCTION"])
        
        self.key_function = key_function
        self.limiter = build_limiter(config=config, backend=backend)
        

    def __call__(self, request):
        key = self.key_function(request)
        decision = self.limiter.check(key)

        if not decision["allowed"]:
            response = HttpResponse("Too many requests", status=429)
            response["Retry-After"] = str(decision["retry_after"])
            return response

        return self.get_response(request)
    