# Proyecto Semilla — Acme SaaS Boilerplate

Boilerplate SaaS moderno basado en Django 5+, con arquitectura modular, multitenancy opcional (schema/db), RBAC granular estilo Discord, onboarding wizard, Stripe memberships, API DRF + OpenAPI, frontend HTMX/Tailwind/Alpine, seguridad endurecida, observabilidad, CI/CD y despliegues reproducibles.

## Requisitos

- Python 3.12+
- Docker + Docker Compose
- Postgres, Redis, MinIO (S3-compatible), Mailpit (via compose)

## Inicio rápido (dev)

```bash
make dev
```

Para seed demo:

```bash
make seed
```

## Salud y métricas

- Liveness: `GET /healthz`
- Readiness: `GET /readyz`
- Prometheus: `GET /metrics`

## Variables de entorno

Plantillas en `env/`:

- `DATABASE_URL`
- `REDIS_URL`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `S3_ENDPOINT_URL`
- `S3_BUCKET_NAME`
- `S3_ACCESS_KEY`
- `S3_SECRET_KEY`
- `SENTRY_DSN`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DJANGO_SECRET_KEY`

## Módulos V1

- `core`
- `multitenant` (schema por defecto)
- `billing`
- `api`
- `oauth`

## Theming por tenant

Cada tenant puede definir branding (colores/logo) vía `Tenant.branding`:

```json
{
  "primary_color": "#4f46e5",
  "logo_url": "https://..."
}
```

Si no se define, se usan valores por defecto.

Módulos opcionales (apagados por feature flags): `cms`, `lms`, `community`, `mcp`.

## Estructura

Ver layout en el prompt base; el código vive en `src/` y settings en `src/config/settings/`.

## Documentación (MkDocs)

La documentación vive en `docs/` y se sirve con MkDocs:

```bash
pip install -r requirements/dev.txt
mkdocs serve
```

## Deploy (Fly.io)

Receta E2E en `deploy/flyio/`:

1. Configura `deploy/flyio/fly.toml` con tu `app` y región.
2. Crea Postgres/Redis y ajusta secretos.
3. Despliega:

```bash
make deploy
```

Detalles en `deploy/flyio/README.md`.

## Licencia

MIT. Ver `LICENSE`.
