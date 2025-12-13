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
- Django: requerido `>=5.0` (en el contenedor actualmente se instaló **Django 6.0** por no estar fijado; ver “Retos”).
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
- Postgres: host `5433` → container `5432`.
- MinIO: `9000` (S3) y `9001` (consola).
- Mailpit: `8025` (UI) y `1025` (SMTP).

Inicialización recomendada (después de levantar):
- Migraciones (public): `docker compose -f compose/docker-compose.yml exec web python manage.py migrate`
- Migraciones por tenant schema: `docker compose -f compose/docker-compose.yml exec web python manage.py migrate_tenants`
- Crear tenant: `docker compose -f compose/docker-compose.yml exec web python manage.py create_tenant "<Org>" <slug>`

## 6) Cambios/ajustes recientes (Docker + arranque)

Para lograr un arranque estable en Docker y exponer `7777`, se aplicaron estos fixes:
- `compose/docker-compose.yml`: `web` en `7777:8000` y Postgres en `5433:5432`.
- `Dockerfile` (stage `dev`): copia `requirements/` completo antes de instalar `requirements/dev.txt`.
- `src/oauth/views.py`: import correcto de rate-limit (`django_ratelimit.decorators`).
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

## 8) Retos actuales / cosas por estabilizar

1) **Django quedó en 6.0** (por `Django>=5.0` sin pin).  
   - Impacto: posibles incompatibilidades y warnings; además contradice la intención “Django 5+ (V1)”.
   - Acción sugerida: fijar `Django~=5.0` (o `<6`) en `requirements/base.txt` y regenerar lock/CI.

2) **`make seed` apunta a `seed_demo`, pero no existe el comando**.  
   - Impacto: DoD de “seed demo” no se cumple con el target actual.
   - Acción sugerida: implementar `manage.py seed_demo` (orquestador) o ajustar `Makefile` para usar `seed_rbac` + `seed_billing` + creación de tenant/admin.

3) **`seed_rbac` no hace schema switch** (en modo `schema`).  
   - Impacto: si se usa el comando, puede sembrar roles/permisos en el schema equivocado.
   - Acción sugerida: iterar tenants desde `public` y ejecutar `seed_default_roles` dentro de `schema_context(tenant.schema_name)`.

4) **Verificación desde host `localhost:7777` en esta automatización**  
   - En esta ejecución automatizada, el “curl” local al puerto host no respondió, pero la verificación *in-container* sí.  
   - Acción sugerida: validar desde máquina del equipo (navegador/curl) y, si falla, revisar firewall/Docker context (Colima/Docker Desktop).

5) **Estado git**  
   - Se hizo “borrón y cuenta nueva” y actualmente hay una gran cantidad de cambios locales pendientes de commit (archivos borrados del histórico previo + nueva estructura sin registrar).
   - Acción sugerida: consolidar el nuevo baseline en un commit limpio y empujar a remoto.

## 9) Checklist de estabilización (recomendado)

- [ ] Pin de versiones críticas (Django 5.x; revisar allauth/django-csp/axes).
- [ ] Implementar `seed_demo` y alinear `Makefile` + README + tests.
- [ ] Confirmar flujo multitenant completo: `create_tenant` → `migrate_tenants` → onboarding → domain routing.
- [ ] Correr `make lint && make typecheck && make test` y corregir regresiones.
- [ ] Validar `localhost:7777` + CSRF en formularios, login/signup (Allauth).
- [ ] Asegurar CI verde y recipe Fly.io E2E.

