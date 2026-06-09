from __future__ import annotations

import hmac

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest


def metrics_view(request):
    """Endpoint Prometheus.

    En producción exige `Authorization: Bearer <METRICS_TOKEN>`. Si
    METRICS_TOKEN no está definido y DEBUG=False, el endpoint queda cerrado:
    las métricas internas no deben ser públicas.
    """
    token = getattr(settings, "METRICS_TOKEN", "")
    if not settings.DEBUG:
        if not token:
            return HttpResponseForbidden("Metrics endpoint disabled (set METRICS_TOKEN).")
        provided = request.headers.get("Authorization", "")
        expected = f"Bearer {token}"
        if not hmac.compare_digest(provided, expected):
            return HttpResponseForbidden("Invalid metrics token.")
    data = generate_latest()
    return HttpResponse(data, content_type=CONTENT_TYPE_LATEST)
