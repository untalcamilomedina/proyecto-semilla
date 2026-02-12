from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.db import connection
from django.core.cache import cache
from django.http import JsonResponse
from django.urls import include, path

from common.metrics import metrics_view
from oauth.views import RateLimitedLoginView, RateLimitedSignupView


def healthz(_request):
    return JsonResponse({"status": "ok"})


def readyz(_request):
    """Readiness probe that verifies database and cache connectivity."""
    checks = {}
    try:
        connection.ensure_connection()
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "fail"

    try:
        cache.set("_health_check", "1", 10)
        checks["cache"] = "ok" if cache.get("_health_check") == "1" else "fail"
    except Exception:
        checks["cache"] = "fail"

    all_ok = all(v == "ok" for v in checks.values())
    return JsonResponse(
        {"status": "ready" if all_ok else "degraded", "checks": checks},
        status=200 if all_ok else 503,
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", RateLimitedLoginView.as_view(), name="account_login"),
    path("accounts/signup/", RateLimitedSignupView.as_view(), name="account_signup"),
    path("accounts/", include("allauth.urls")),
    path("healthz", healthz),
    path("readyz", readyz),
    path("metrics", metrics_view),
    # Note: /healthz and /readyz provide custom health checks above
    path("api/", include("api.urls")),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path("billing/", include("billing.urls")),
    path("", include("core.urls")),
]

# Debug-only endpoints -- never exposed in production
if settings.DEBUG:
    import logging

    def trigger_error(request):
        logger = logging.getLogger(__name__)
        logger.error("Test JSON Logging Error")
        try:
            1 / 0
        except ZeroDivisionError:
            logger.exception("Test Exception Capture")
            if request.GET.get("raise"):
                raise
        return JsonResponse({"status": "error_logged"})

    urlpatterns += [
        path("debug/error/", trigger_error),
        path("silk/", include("silk.urls", namespace="silk")),
    ]
