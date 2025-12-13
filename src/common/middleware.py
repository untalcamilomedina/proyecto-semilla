from __future__ import annotations

import time

from django.utils.deprecation import MiddlewareMixin
from prometheus_client import Counter, Histogram


REQUEST_COUNT = Counter(
    "django_http_requests_total",
    "Total HTTP requests",
    ["method", "route", "status"],
)
REQUEST_LATENCY = Histogram(
    "django_http_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "route"],
)


class MetricsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._metrics_start_time = time.monotonic()  # type: ignore[attr-defined]

    def process_response(self, request, response):
        try:
            start = getattr(request, "_metrics_start_time", None)
            if start is None:
                return response
            duration = time.monotonic() - start
            match = getattr(request, "resolver_match", None)
            route = getattr(match, "route", None) or request.path_info
            REQUEST_LATENCY.labels(request.method, route).observe(duration)
            REQUEST_COUNT.labels(request.method, route, str(response.status_code)).inc()
        except Exception:
            pass
        return response

