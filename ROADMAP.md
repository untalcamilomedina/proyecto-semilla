# Roadmap / Bitácora de avance – Proyecto Semilla

Este documento registra cambios recientes, hallazgos y pendientes del boilerplate `proyecto-semilla`.

## Última intervención: Docker (dev) + arranque en puerto 7777

### Objetivo
- Revisar configuración actual de Docker/Compose.
- Levantar el sistema en Docker y exponerlo en `localhost:7777` para pruebas rápidas.

### Cambios realizados
- `compose/docker-compose.yml`
  - `web` expuesto en host `7777:8000`.
  - `postgres` expuesto en host `5433:5432` para evitar colisión local con `5432`.
- `Dockerfile`
  - Fix en stage `dev`: copiar `requirements/` completo antes de instalar `requirements/dev.txt` (porque incluye `-r base.txt`).
- `src/config/settings/base.py`
  - Se añadió `allauth.account.middleware.AccountMiddleware` a `MIDDLEWARE` (requerido por Allauth).
  - Se añadió `csp.middleware.CSPMiddleware` y se migró configuración de CSP al formato de `django-csp==4.x`.
  - Se corrigió `ROOT_DIR` (estaba resolviendo a `/` en contenedor) para que rutas como `STATICFILES_DIRS` apunten a `.../src/static`.
  - Se actualizaron settings de Allauth a la nueva API (`ACCOUNT_LOGIN_METHODS`, `ACCOUNT_SIGNUP_FIELDS`).
  - Se incluyó configuración recomendada de Axes (`axes.middleware.AxesMiddleware` y `axes.backends.AxesStandaloneBackend`), manteniendo `AXES_ENABLED` como flag.
- `src/oauth/views.py`
  - Fix de import de rate-limit: `ratelimit.decorators` → `django_ratelimit.decorators` (paquete instalado expone `django_ratelimit`).
- `src/core/admin.py`
  - Fix de `admin.E013`: se reemplazó `filter_horizontal=("permissions",)` por `RolePermissionInline` (la relación usa `through=RolePermission`).
- `src/static/.gitkeep`
  - Se crea el directorio `src/static/` para evitar warnings de `STATICFILES_DIRS`.

### Problemas encontrados (y cómo se resolvieron)
- `ModuleNotFoundError: No module named 'ratelimit'`
  - Causa: `django-ratelimit` expone `django_ratelimit`, no `ratelimit`.
  - Solución: actualizar import en `src/oauth/views.py`.
- `admin.E013` en `core.admin.RoleAdmin`
  - Causa: `filter_horizontal` no soporta `ManyToManyField` con `through`.
  - Solución: inline `RolePermissionInline`.
- `csp.E001` (migración requerida por `django-csp==4.0`)
  - Causa: settings legacy `CSP_*`.
  - Solución: usar `CONTENT_SECURITY_POLICY{_REPORT_ONLY}` con `DIRECTIVES`.
- Rutas estáticas incorrectas en contenedor (`/src/static` inexistente)
  - Causa: `ROOT_DIR` calculado con `parents[4]` (en `/app/...` terminaba en `/`).
  - Solución: `ROOT_DIR = ...parents[3]` + creación de `src/static/`.
- Docker build (dev) fallaba al instalar requirements
  - Causa: se copiaba solo `requirements/dev.txt`, pero este incluye `-r base.txt`.
  - Solución: copiar `requirements/` completo antes de `pip install`.
- Allauth fallaba por middleware faltante
  - Solución: añadir `allauth.account.middleware.AccountMiddleware`.

### Estado actual (Docker dev)
- El servicio `web` inicia correctamente dentro del contenedor y responde:
  - `GET /healthz` → `{"status":"ok"}`
  - `GET /readyz` → `{"status":"ready"}`
- Puerto host configurado: `http://localhost:7777/`

### Notas / pendientes inmediatos
- Django reporta migraciones no aplicadas (esperable en un entorno dev recién levantado). Para inicializar:
  - `docker compose -f compose/docker-compose.yml exec web python manage.py migrate`
  - Si usas multitenancy schema: `docker compose -f compose/docker-compose.yml exec web python manage.py migrate_tenants`
  - Seed demo: `docker compose -f compose/docker-compose.yml exec web python manage.py seed_demo`

