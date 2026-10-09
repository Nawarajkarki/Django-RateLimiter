import pytest

from django.core.exceptions import ImproperlyConfigured

from django_ratelimiter.backends.memory import MemoryBackend
from django_ratelimiter.core.limiter import build_limiter
from django_ratelimiter.core.algorithms.fixed_window import FixedWindow
from django_ratelimiter.core.algorithms.sliding_window_counter import SlidingWindowCounter


def test_builds_fixed_window():
    backend = MemoryBackend()
    config = {
        "ALGORITHM": "fixed_window",
        "LIMIT": 2,
        "WINDOW_SECONDS": 60,
    }

    limiter = build_limiter(config, backend)

    assert isinstance(limiter, FixedWindow)
    assert limiter.backend is backend



@pytest.mark.parametrize("algorithm", [ "sliding_window", "token_bucket", "anything else"])
def test_build_limiter_rejects_unimplemented_algorithms(algorithm):
    config = {
        "ALGORITHM": algorithm,
        "LIMIT": 2,
        "WINDOW_SECONDS": 60,
    }

    with pytest.raises(ImproperlyConfigured, match="Unsupported rate-limit algorithm"):
        build_limiter(config=config, backend=MemoryBackend())



def test_builds_sliding_window_counter():
    backend = MemoryBackend()
    config = {
        "ALGORITHM": "sliding_window_counter",
        "LIMIT": 2,
        "WINDOW_SECONDS": 60,
    }

    limiter = build_limiter(config, backend)

    assert isinstance(limiter, SlidingWindowCounter)
    assert limiter.backend is backend