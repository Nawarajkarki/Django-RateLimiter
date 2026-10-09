from django.core.exceptions import ImproperlyConfigured

from django_ratelimiter.core.algorithms.fixed_window import FixedWindow



def build_limiter(config, backend):
    algorithm = config["ALGORITHM"]

    
    normalized_algo = algorithm.lower().strip().replace("-", "_").replace(" ", "_")
    
    if normalized_algo == "fixed_window":
        return FixedWindow(
            limit=config["LIMIT"],
            window_size=config["WINDOW_SECONDS"],
            backend=backend,
        )

    # elif normalized_algo == "sliding_window":
        
    #     pass
    
    # elif normalized_algo == "token_bucket":
        
    #     pass
    
    
    raise ImproperlyConfigured(f"Unsupported rate-limit algorithm: {algorithm}")