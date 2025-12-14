# Proyecto Semilla — Resumen para estabilización (handoff)

Este repositorio es un boilerplate SaaS moderno basado en Django, orientado a multitenancy (schema por defecto), RBAC granular estilo Discord, onboarding wizard, billing/memberships con Stripe, API con DRF + OpenAPI, frontend HTMX/Tailwind/Alpine, seguridad endurecida, observabilidad y despliegue reproducible (Fly.io).

## 1) Objetivo y alcance (V1)

**Incluido en V1 (activo):**
- `core`: usuarios, organizaciones/tenants, memberships, roles, permisos y onboarding.
- `multitenant`: modo `schema` (public + tenant schemas), middleware host→tenant y comandos de gestión.
- `billing`: modelos de planes/precios/suscripciones, servicios Stripe (checkout/portal/webhooks), límites por seats.
- `api`: DRF versionado `/api/v1`, auth por API key por tenant + session, OpenAPI (drf-spectacular).
- `oauth`: django-allauth y endpoints de auth con rate-limit.

**Scaffolding presente pero apagado (feature flags):**
- `cms` (Wagtail), `lms`, `community`, `mcp`.

## 2) Stack y dependencias clave

- Python: `3.12` (Docker base: `python:3.12-slim`).
- Django: `>=5.0,<6.0` (actual: `5.2.9`; ver `requirements/base.txt`).
- DB/Cache: Postgres + Redis.
- Jobs: Celery (`worker` + `beat` en compose).
- S3-compatible: MinIO (dev) vía `django-storages`.
- Email dev: Mailpit.
- Observabilidad: Sentry (opcional), `/healthz`, `/readyz`, `/metrics` (Prometheus).
- Seguridad: `django-csp`, `django-axes` (habilitable), `django-ratelimit`.
- DX/Calidad: `ruff`, `black`, `isort`, `bandit`, `djlint`, `mypy`, `pip-audit`, `safety`, `pytest` con cobertura mínima `90%`.

## 3) Estructura del repo (high level)

- `src/config/settings/`: settings `base.py`, `dev.py`, `prod.py` + `plugins.py` (feature flags).
- `src/multitenant/`: schema switching (`search_path`), modelos `Tenant/Domain`, middleware, comandos.
- `src/core/`: modelos RBAC, servicios de onboarding/seed, vistas HTMX y UI roles.
- `src/billing/`: servicios Stripe, webhooks, límites por seats, seed de planes demo.
- `src/api/`: autenticación por API key por tenant, routers DRF y OpenAPI.
- `frontend/`: app Next.js (React) para migración gradual; proxy `/api/*` → Django vía `rewrites`.
- `compose/docker-compose.yml`: stack dev (web/worker/beat + postgres/redis/minio/mailpit).
- `deploy/flyio/`: receta de deploy E2E (Fly.io).
- `docs/` + `mkdocs.yml`: documentación (arquitectura/runbooks/ADRs).
- `.github/workflows/`: CI (lint/type/test/coverage/build).

## 4) Configuración por variables de entorno

Plantillas:
- `env/.env.dev.example`
- `env/.env.prod.example`

Variables principales (mínimo):
- `DJANGO_SECRET_KEY`, `DEBUG`
- `DATABASE_URL`, `REDIS_URL`
- `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DOMAIN_BASE`
- `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- `S3_ENDPOINT_URL`, `S3_BUCKET_NAME`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`
- `SENTRY_DSN`

Flags:
- `MULTITENANT_MODE=off|schema|database` (default: `schema`) en `src/config/settings/plugins.py`.
- `ENABLE_CMS`, `ENABLE_LMS`, `ENABLE_COMMUNITY`, `ENABLE_MCP` (default: `False`).
- `ENABLE_AXES` (default: `not DEBUG`).

## 5) Ejecución local (Docker) y puertos

Comandos (Makefile):
- `make dev`: levanta todo con Docker Compose.
- `make build`: build de imagen.
- `make lint`, `make fmt`, `make typecheck`, `make test`.

Compose: `compose/docker-compose.yml`
- Web: `http://localhost:7777` (mapea `7777:8000`).
- Frontend (Next.js): `http://localhost:3000` (mapea `3000:3000`).
  - En dev, el navegador consume `/api/...` en el mismo origen del frontend (proxy por `rewrites`, sin CORS).
- Postgres: host `5433` → container `5432`.
- MinIO: `9000` (S3) y `9001` (consola).
- Mailpit: `8025` (UI) y `1025` (SMTP).
  - Si el puerto `3000` está ocupado: `FRONTEND_PORT=3001 make dev`.

Inicialización recomendada (después de levantar):
- Migraciones (public): `docker compose -f compose/docker-compose.yml exec web python manage.py migrate`
- Migraciones por tenant schema: `docker compose -f compose/docker-compose.yml exec web python manage.py migrate_tenants`
- Seed demo (recomendado): `make seed` (crea tenant demo + dominios `localhost/127.0.0.1` + usuario demo)
- Crear tenant: `docker compose -f compose/docker-compose.yml exec web python manage.py create_tenant "<Org>" <slug>`

## 6) Cambios/ajustes recientes (Docker + arranque)

Para lograr un arranque estable en Docker y exponer `7777`, se aplicaron estos fixes:
- `compose/docker-compose.yml`: `web` en `7777:8000`, `frontend` en `3000:3000` y Postgres en `5433:5432`.
- `Dockerfile` (stage `dev`): copia `requirements/` completo antes de instalar `requirements/dev.txt`.
- `src/oauth/views.py`: import correcto de rate-limit (`django_ratelimit.decorators`).
- `src/config/settings/dev.py`: `ALLOWED_HOSTS` desde env y `USE_X_FORWARDED_HOST=1` para correr detrás del proxy/rewrite de Next.js en Docker.
- `src/config/settings/base.py`:
  - `AccountMiddleware` (Allauth) agregado.
  - CSP migrado a formato `django-csp==4.x` y `CSPMiddleware` agregado.
  - `ROOT_DIR` corregido (evita rutas rotas dentro del contenedor).
  - Settings de Allauth actualizados a API nueva.
  - Axes backend + middleware configurados.
- `src/core/admin.py`: fix `admin.E013` (M2M con `through`) usando inline `RolePermissionInline`.
- `src/static/.gitkeep`: asegura existencia de `src/static/` para `STATICFILES_DIRS`.

## 7) Estado actual (verificación)

- Dentro del contenedor, el servidor responde correctamente:
  - `GET /healthz` → `{"status":"ok"}`
  - `GET /readyz` → `{"status":"ready"}`
- Se observó aviso de “unapplied migrations” al levantar por primera vez (normal si no se ha corrido `migrate`).
- Frontend Next.js de prueba: `http://localhost:3000/` (o `3001`) permite verificar `GET /api/v1/csrf` y `GET /api/v1/tenant` (requiere login en Django).

## 8) Retos actuales / cosas por estabilizar (v0.9.1)

### ✅ Resuelto (v0.9.0)

- Django fijado a `>=5.0,<6.0`.
- `seed_demo` implementado y `seed_rbac` con schema switching correcto.

### 🔄 Pendiente / recomendado

1) **Calidad: tests y cobertura**
   - Estado: cobertura reportada ~58% (objetivo: 90%) y tests fallando.
   - Acción sugerida: priorizar tests de multitenancy, API v1 y billing webhooks.

2) **OpenAPI (drf-spectacular)**
   - Estado: suelen aparecer warnings si falta metadata/serializers en views.
   - Acción sugerida: mantener viewsets con `serializer_class` y documentar auth custom.

3) **Seguridad de producción (checks)**
   - Estado: `check --deploy` requiere HSTS/SSL redirect/cookies seguras (ya está en `settings/prod.py`).
   - Acción sugerida: completar variables/secretos en deploy y validar headers.

4) **Migración de frontend HTMX → Next.js**
   - Estado: ver `docs/runbooks/migracion-frontend-nextjs.md` (v0.9.1).
   - Acción sugerida: migrar primero `dashboard`, `members`, `roles`, `billing` consumiendo `/api/v1`.

## 9) Checklist recomendado (v0.9.1)

- [ ] Ejecutar `make lint && make typecheck && make test` y corregir regresiones.
- [ ] Validar auth end-to-end (login/signup) y acceso a `/api/v1` con sesión.
- [ ] Revisar `/api/docs/` y corregir warnings restantes de OpenAPI.
- [ ] Arrancar migración Next.js siguiendo `docs/runbooks/migracion-frontend-nextjs.md`.

## 10) Próximos pasos (para el equipo) — comandos

1) Levantar stack (build incluido):
   - `make dev`

2) Inicializar DB (primera vez o cuando cambien migraciones):
   - `docker compose -f compose/docker-compose.yml exec web python manage.py migrate`
   - `docker compose -f compose/docker-compose.yml exec web python manage.py migrate_tenants`

3) Crear entorno demo:
   - `make seed`
   - Credenciales: `admin@demo.com` / `password`

4) Verificar URLs:
   - Django: `http://localhost:7777/` (tenant demo por `localhost`)
   - Frontend: `http://localhost:3000/` (si está ocupado: `http://localhost:3001/` con `FRONTEND_PORT=3001`)
   - API docs: `http://localhost:7777/api/docs/`
   - Health: `http://localhost:7777/healthz`

5) Iniciar migración de pantallas (orden sugerido):
   - Dashboard → Members → Roles → Billing (consumiendo `/api/v1`)
   - CSRF para mutaciones: `GET /api/v1/csrf/` y header `X-CSRFToken`

## 11) Troubleshooting rápido (v0.9.1)

- Si ves `DisallowedHost: 'web:8000'` al consumir `/api/...` desde Next.js:
  - Verifica `env/.env.dev.example` incluye `USE_X_FORWARDED_HOST=1` y `ALLOWED_HOSTS=...,web,...`
  - Reinicia: `docker compose -f compose/docker-compose.yml restart web frontend`
- Si hay redirects/loops por slash final en `/api/v1/...`:
  - La API v1 acepta rutas con o sin slash final (compatibilidad para proxies); valida `frontend/next.config.ts` y usa `/api/v1/...` o `/api/v1/.../` de forma consistente.
