# Observability

V1 incluye endpoints de salud, métricas Prometheus y Sentry opcional.

## Endpoints

- `GET /healthz` — liveness.
- `GET /readyz` — readiness.
- `GET /metrics` — métricas Prometheus.

## Métricas

El middleware `common.middleware.MetricsMiddleware` exporta:

- `django_http_requests_total{method,route,status}`
- `django_http_request_latency_seconds{method,route}`

## Sentry

Si `SENTRY_DSN` está configurado, Sentry se inicializa automáticamente en `src/config/settings/base.py`.

Variables útiles:

- `SENTRY_DSN`
- `SENTRY_ENVIRONMENT` (default: `dev`/`prod`)
- `SENTRY_RELEASE`
- `SENTRY_TRACES_SAMPLE_RATE`

