# Proyecto Semilla — Acme SaaS Boilerplate

[![Version](https://img.shields.io/badge/version-0.9.1-blue.svg)](https://github.com/untalcamilomedina/proyecto-semilla/releases)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.2.9-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Boilerplate SaaS moderno basado en Django 5+, con arquitectura modular, multitenancy opcional (schema/db), RBAC granular estilo Discord, onboarding wizard, Stripe memberships, API DRF + OpenAPI, frontend HTMX/Tailwind/Alpine, seguridad endurecida, observabilidad, CI/CD y despliegues reproducibles.

**Versión actual:** `v0.9.1` - Estable y funcional

> ⚠️ **Nota:** Esta es una versión pre-1.0. El sistema es funcional y estable, pero algunos tests están pendientes de corrección y la cobertura de tests está en 58.57% (objetivo: 90%).

## Requisitos

- Python 3.12+
- Docker + Docker Compose
- Postgres, Redis, MinIO (S3-compatible), Mailpit (via compose)

## Inicio rápido (dev)

### 1. Levantar servicios

```bash
make dev
```

Esto levantará todos los servicios Docker:
- **Web:** `http://localhost:7777`
- **Frontend:** `http://localhost:3000`
- **Postgres:** `localhost:5433`
- **Redis:** `localhost:6380`
- **MinIO:** `http://localhost:9000` (S3) y `http://localhost:9001` (consola)
- **Mailpit:** `http://localhost:8025` (UI) y `localhost:1025` (SMTP)

> Si el puerto `3000` está ocupado, usa `FRONTEND_PORT=3001 make dev`.

### 2. Aplicar migraciones

```bash
# Migraciones del schema public
docker compose -f compose/docker-compose.yml exec web python manage.py migrate

# Migraciones por tenant schema
docker compose -f compose/docker-compose.yml exec web python manage.py migrate_tenants
```

### 3. Seed demo (opcional)

```bash
make seed
# O directamente:
docker compose -f compose/docker-compose.yml exec web python manage.py seed_demo
```

Esto creará:
- Tenant "demo" con dominio `demo.acme.dev`
- Usuario `admin@demo.com` / `password`
- Roles y permisos por defecto
- Planes de billing demo

## Frontend (migración a Next.js)

La migración de HTMX → React + Next.js se documenta en `docs/runbooks/migracion-frontend-nextjs.md` (v0.9.1).

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

## Estructura del Proyecto

```
proyecto-semilla/
├── src/                    # Código fuente
│   ├── config/             # Settings (base, dev, prod, plugins)
│   ├── core/               # Usuarios, RBAC, onboarding
│   ├── multitenant/        # Multitenancy (schema mode)
│   ├── billing/            # Stripe, planes, suscripciones
│   ├── api/                # DRF + OpenAPI
│   └── oauth/              # django-allauth
├── compose/                 # Docker Compose
├── deploy/                 # Recetas de despliegue (Fly.io)
├── docs/                   # Documentación (MkDocs)
├── tests/                  # Tests
└── requirements/           # Dependencias (base, dev, prod)
```

Ver más detalles en [docs/architecture.md](docs/architecture.md).

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

## Estado del Proyecto

### ✅ Funcionalidades V1 (Operativas)
- ✅ Multitenancy en modo schema
- ✅ RBAC granular (roles y permisos)
- ✅ Onboarding wizard
- ✅ Billing con Stripe (checkout, portal, webhooks)
- ✅ API REST con DRF + OpenAPI
- ✅ Autenticación (django-allauth)
- ✅ Health checks y métricas

### 🔄 En Desarrollo
- ⚠️ Tests: 14 pasando, 6 fallando
- ⚠️ Cobertura: 58.57% (objetivo: 90%)
- ⚠️ Documentación OpenAPI: algunos warnings menores

### 📋 Próximos Pasos
Ver [ROADMAP.md](ROADMAP.md) y [RESUMEN_PROYECTO.md](RESUMEN_PROYECTO.md) para detalles.

## Comandos Útiles

```bash
# Desarrollo
make dev              # Levantar servicios
make seed             # Seed demo
make lint             # Linting
make fmt              # Formatear código
make typecheck        # Type checking
make test             # Ejecutar tests

# Gestión de tenants
docker compose -f compose/docker-compose.yml exec web python manage.py create_tenant "Nombre" slug
docker compose -f compose/docker-compose.yml exec web python manage.py list_tenants
docker compose -f compose/docker-compose.yml exec web python manage.py migrate_tenants
```

## Documentación

- **Arquitectura:** [docs/architecture.md](docs/architecture.md)
- **Multitenancy:** [docs/multitenancy.md](docs/multitenancy.md)
- **Billing:** [docs/billing.md](docs/billing.md)
- **RBAC:** [docs/rbac.md](docs/rbac.md)
- **Runbooks:** [docs/runbooks/](docs/runbooks/)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

## Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guías de contribución.

## Licencia

MIT. Ver [LICENSE](LICENSE).
