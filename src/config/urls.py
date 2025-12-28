from __future__ import annotations

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from common.metrics import metrics_view
from oauth.views import RateLimitedLoginView, RateLimitedSignupView


def healthz(_request):
    return JsonResponse({"status": "ok"})


def readyz(_request):
    return JsonResponse({"status": "ready"})

def trigger_error(request):
    import logging
    logger = logging.getLogger(__name__)
    logger.error("Test JSON Logging Error")
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("Test Exception Capture")
        if request.GET.get("raise"):
            raise
    return JsonResponse({"status": "error_logged"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", RateLimitedLoginView.as_view(), name="account_login"),
    path("accounts/signup/", RateLimitedSignupView.as_view(), name="account_signup"),
    path("accounts/", include("allauth.urls")),
    path("healthz", healthz),
    path("readyz", readyz),
    path("debug/error/", trigger_error),
    path("metrics", metrics_view),
    path("ht/", include("health_check.urls")),
    path("api/", include("api.urls")),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path("silk/", include("silk.urls", namespace="silk")),
    path("billing/", include("billing.urls")),
    path("", include("core.urls")),
]
