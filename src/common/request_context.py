"""Correlación de requests para observabilidad.

- `RequestContextMiddleware`: asigna/propaga `X-Request-ID` y publica
  request_id + tenant en contextvars (seguro para async y threads).
- `RequestContextFilter`: inyecta esos campos en CADA registro de log, de modo
  que los logs JSON quedan correlacionables por request y por tenant.

Colócalo después de TenantMiddleware (necesita request.tenant resuelto).
"""

from __future__ import annotations

import logging
import uuid
from contextvars import ContextVar

_request_id: ContextVar[str] = ContextVar("request_id", default="-")
_tenant_slug: ContextVar[str] = ContextVar("tenant_slug", default="-")

REQUEST_ID_HEADER = "X-Request-ID"


def get_request_id() -> str:
    return _request_id.get()


class RequestContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        incoming = request.headers.get(REQUEST_ID_HEADER, "")
        # Acepta el ID del proxy/cliente si es razonable; si no, genera uno.
        request_id = incoming[:64] if incoming and incoming.isascii() else uuid.uuid4().hex[:16]
        token_id = _request_id.set(request_id)

        tenant = getattr(request, "tenant", None)
        token_tenant = _tenant_slug.set(getattr(tenant, "slug", None) or "-")

        request.request_id = request_id
        try:
            response = self.get_response(request)
        finally:
            _request_id.reset(token_id)
            _tenant_slug.reset(token_tenant)
        response[REQUEST_ID_HEADER] = request_id
        return response


class RequestContextFilter(logging.Filter):
    """Añade request_id y tenant a todos los registros (\"-\" fuera de un request)."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id.get()
        record.tenant = _tenant_slug.get()
        return True
