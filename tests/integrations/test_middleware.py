from django.http import HttpResponse
from django.test import RequestFactory


from django_ratelimiter.integrations.middleware import RateLimitMiddleware

def configure_test_middleware(settings, monkeypatch, *, limit):
    settings.RATE_LIMITER = {
        "ALGORITHM": "fixed_window",
        "LIMIT": limit,
        "WINDOW_SECONDS": 60,
        "KEY_FUNCTION": "unused.in.test",
    }

    # Keep the clock fixed so requests stay in the same window.
    monkeypatch.setattr(
        "django_ratelimiter.core.algorithms.fixed_window.time",
        lambda: 1000,
    )

    # Give every request from this test client the same rate-limit key.
    monkeypatch.setattr(
        "django_ratelimiter.integrations.middleware.import_string",
        lambda dotted_path: lambda request: "ip:127.0.0.1",
    )


def test_allowed_request_reaches_view(settings, monkeypatch):
    configure_test_middleware(settings, monkeypatch, limit=1)
    view_calls = []

    def get_response(request):
        view_calls.append(request)
        return HttpResponse("View response")

    middleware = RateLimitMiddleware(get_response)
    request = RequestFactory().get("/")

    response = middleware(request)

    assert response.status_code == 200
    assert len(view_calls) == 1


def test_rejected_request_returns_429_and_does_not_reach_view(
    settings, monkeypatch
):
    configure_test_middleware(settings, monkeypatch, limit=1)
    view_calls = []

    def get_response(request):
        view_calls.append(request)
        return HttpResponse("View response")

    middleware = RateLimitMiddleware(get_response)
    request = RequestFactory().get("/")

    first_response = middleware(request)
    second_response = middleware(request)

    assert first_response.status_code == 200
    assert second_response.status_code == 429
    assert second_response["Retry-After"] == "20"
    assert len(view_calls) == 1