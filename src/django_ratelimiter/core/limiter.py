from django.core.exceptions import ImproperlyConfigured

from django_ratelimiter.core.algorithms.fixed_window import FixedWindow
from django_ratelimiter.core.algorithms.sliding_window_counter import SlidingWindowCounter



def build_limiter(config, backend):
    algorithm = config["ALGORITHM"]

    
    normalized_algo = algorithm.lower().strip().replace("-", "_").replace(" ", "_")
    
    if normalized_algo == "fixed_window":
        return FixedWindow(
            limit=config["LIMIT"],
            window_size=config["WINDOW_SECONDS"],
            backend=backend,
        )

    elif normalized_algo == "sliding_window_counter":
        return SlidingWindowCounter(
            limit = config["LIMIT"],
            window_size = config["WINDOW_SECONDS"],
            backend = backend
        )
    
    # elif normalized_algo == "token_bucket":
        
    #     pass
    
    
    raise ImproperlyConfigured(f"Unsupported rate-limit algorithm: {algorithm}")