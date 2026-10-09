
import uuid

import pytest
from redis import Redis
from concurrent.futures import ThreadPoolExecutor

from django_ratelimiter.backends.redis import RedisBackend
from django_ratelimiter.core.algorithms.fixed_window import FixedWindow


@pytest.fixture
def redis_backend():
    client = Redis(
        host="localhost",
        port=6379,
        db=15,
        protocol=2,
        decode_responses=True,
    )
    client.ping()

    prefix = f"test-ratelimiter-{uuid.uuid4().hex}"
    backend = RedisBackend(client, key_prefix=prefix)

    yield backend

    keys = list(client.scan_iter(match=f"{prefix}:*"))
    if keys:
        client.delete(*keys)
    client.close()
    
    
def test_missing_key_returns_none(redis_backend):
    assert redis_backend.get("missing") is None


def test_set_and_get_round_trip(redis_backend):
    state = {"window_id": 12, "request_count": 2}

    redis_backend.set("client-1", state)

    assert redis_backend.get("client-1") == state


def test_set_applies_timeout(redis_backend):
    redis_backend.set("client-1", {"request_count": 1}, timeout=2)

    ttl = redis_backend.client.ttl(redis_backend._redis_key("client-1"))
    assert 0 < ttl <= 2
    
    
    


def test_fixed_window_uses_redis_backend(redis_backend, monkeypatch):
    monkeypatch.setattr(
        "django_ratelimiter.core.algorithms.fixed_window.time",
        lambda: 1000,
    )

    limiter = FixedWindow(
        limit=2,
        window_size=60,
        backend=redis_backend,
    )

    assert limiter.check("client-1") == {"allowed": True}
    assert limiter.check("client-1") == {"allowed": True}
    assert limiter.check("client-1") == {
        "allowed": False,
        "retry_after": 20,
    }

    state = redis_backend.get("client-1")
    assert state == {"window_id": 16, "request_count": 2}
    
    
    


def test_concurrent_requests_do_not_exceed_limit_with_redis(
    redis_backend,
    monkeypatch,
):
    monkeypatch.setattr(
        "django_ratelimiter.core.algorithms.fixed_window.time",
        lambda: 1000,
    )

    limit = 10
    limiter = FixedWindow(
        limit=limit,
        window_size=60,
        backend=redis_backend,
    )

    with ThreadPoolExecutor(max_workers=20) as executor:
        decisions = list(
            executor.map(
                lambda _: limiter.check("client-1"),
                range(100),
            )
        )

    allowed_count = sum(decision["allowed"] for decision in decisions)
    assert allowed_count == limit

    state = redis_backend.get("client-1")
    assert state is not None
    assert state["request_count"] == limit