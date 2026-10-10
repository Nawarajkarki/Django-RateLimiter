import pytest
from django.http import HttpResponse
from django.conf import settings

from django_ratelimiter.integrations.decorator import parse_rate_string, rate_limit
from django_ratelimiter.backends.memory import MemoryBackend


def dummy_key_func(request):
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


@pytest.mark.parametrize(
    ("rate_string", "expected"),
    [
        ("10/s", (10, 1)),
        ("10/30s", (10, 30)),
        ("5/5min", (5, 300)),
        ("100/2h", (100, 7200)),
        (" 10 / MIN ", (10, 60)),
    ],
)
def test_parse_rate_string_valid_values(rate_string, expected):
    assert parse_rate_string(rate_string) == expected


@pytest.mark.parametrize("rate_string", ["", "abc", "10", "10/x", "0/s", "10/0s"])
def test_parse_rate_string_rejects_invalid_values(rate_string):
    with pytest.raises(ValueError):
        parse_rate_string(rate_string)


@pytest.mark.parametrize("rate_string", [None, 10])
def test_parse_rate_string_requires_string(rate_string):
    with pytest.raises(TypeError):
        parse_rate_string(rate_string)


@pytest.fixture(autouse=True)
def rate_limiter_settings(settings):
    settings.RATE_LIMITER = {
        "BACKEND" : "memory",
        "ALGORITHM" : "fixed_window",
        "LIMIT" : 2,
        "WINDOW_SECONDS" : 60,
        "KEY_FUNCTION" : "tests.integrations.test_decorator.dummy_key_func"
    }
    

@pytest.mark.django_db
def test_decorator_allows_requests_within_limit(rf):
    @rate_limit()
    def sample_view(request):
        return HttpResponse("ok", status=200)
    
    request = rf.get('/test/')
    
    response1 = sample_view(request)
    assert response1.status_code == 200
    assert response1.content.decode() == 'ok'

    
    response2 = sample_view(request)
    assert response2.status_code == 200
    assert response2.content.decode() == "ok"

    
@pytest.mark.django_db
def test_decorator_blocks_exceeded_limit(rf):
    @rate_limit()
    def sample_view(request):
        return HttpResponse("ok", status=200)

    request = rf.get('/test')

    assert sample_view(request).status_code == 200
    assert sample_view(request).status_code == 200
    
    response = sample_view(request)
    assert response is not None
    assert response.status_code == 429
    assert response.content.decode() == 'Too many requests'
    assert response['RETRY-AFTER'] is not None
    

@pytest.mark.django_db
def test_decorator_per_view_overrides(rf):
    @rate_limit("1/30s")
    def strict_view(request):
        return HttpResponse("secret", status=200)

    request = rf.get('/strict')
    
    response1 = strict_view(request)
    assert response1.status_code == 200

    response2 = strict_view(request)
    assert response2.status_code == 429
    

def test_per_view_override_does_not_change_settings(settings):
    original_config = settings.RATE_LIMITER.copy()

    @rate_limit("1/30s")
    def strict_view(request):
        return HttpResponse("ok")

    assert settings.RATE_LIMITER == original_config
    
    




def test_each_view_has_its_own_limit(monkeypatch, rf):
    shared_backend = MemoryBackend()
    monkeypatch.setattr(
        "django_ratelimiter.integrations.decorator.build_backend",
        lambda config: shared_backend,
    )

    @rate_limit("1/m")
    def view_a(request):
        return HttpResponse("A")

    @rate_limit("1/m")
    def view_b(request):
        return HttpResponse("B")

    request = rf.get("/")

    assert view_a(request).status_code == 200
    assert view_b(request).status_code == 200  # Different view scope
    assert view_a(request).status_code == 429



def test_decorator_uses_sliding_window_counter(settings, monkeypatch, rf):
    settings.RATE_LIMITER = {
        **settings.RATE_LIMITER,
        "ALGORITHM": "sliding_window_counter",
        "LIMIT": 2,
    }

    monkeypatch.setattr(
        "django_ratelimiter.core.algorithms.sliding_window_counter.time",
        lambda: 1000,
    )

    @rate_limit()
    def sample_view(request):
        return HttpResponse("ok")

    request = rf.get("/")

    assert sample_view(request).status_code == 200
    assert sample_view(request).status_code == 200
    assert sample_view(request).status_code == 429
