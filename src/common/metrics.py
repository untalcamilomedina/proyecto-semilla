from __future__ import annotations

from django.http import HttpResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest


def metrics_view(_request):
    data = generate_latest()
    return HttpResponse(data, content_type=CONTENT_TYPE_LATEST)

