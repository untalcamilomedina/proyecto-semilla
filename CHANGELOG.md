# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## v0.10.4 - (2025-12-28)

### Added
- **Observability**: Enabled JSON Logging by default (via `python-json-logger`).
- **Debugging**: Added `/debug/error/` endpoint for Sentry testing (Dev only).
- **Documentation**: Updated `AGENTS.md` with "Vibe Coding" standards and Design System specs.
- **Frontend**: Initialized Next.js 16 project with Glass UI Design System (Neon Green).

## v0.10.3 - (2025-12-27)

### Added
- **Observability**: Added `django-health-check` endpoint at `/ht/`.
- **Infrastructure**: Health checks valid for DB, Redis Cache, Storage (S3/MinIO), and Migrations.
- **Compliance**: "Enterprise Readiness" achieved via standard health probes.

## v0.10.2 - (2025-12-27)

### Added
- **Infrastructure**: Switched cache backend to `django-redis` for production-grade caching.
- **Session**: Configured `SESSION_ENGINE` to use Redis (Stateless backend).
- **Performance**: Implemented 5-minute caching for `DashboardViewSet` stats.
- **Security**: Configured `Axes` to use Redis for rate limiting storage.

## v0.10.1 - (2025-12-27)

### Fixed
- **Performance**: Optimized `DashboardViewSet` to use real, efficient queries.
    - Replaced hardcoded data with `Membership` counts.
    - Added `select_related` to `RoleAuditLog` queries to prevent N+1 issues.
- **API**: `MembershipViewSet` verified to use `select_related("user", "role")`.

## v0.10.0 - (2025-12-27)

### Added
- **Performance**: Integrated `django-silk` for request profiling and query optimization.
- **Monitoring**: Enabled `SILKY_PYTHON_PROFILER` to track execution time and DB queries.
- **Docs**: Updated `AGENTS.md` with performance standards.

## v0.9.4 - (2025-12-27)

### Added
- **Email Transactional**: Integration with `django-anymail` for robust email delivery.
- **EmailService**: Abstraction layer for sending emails (`src/core/services/email.py`).
- **Templates**: HTML and TXT templates for Welcome and Invite emails.
- **Integration**:
    - Automatic welcome email upon Onboarding completion.
    - Invitation emails sent via `MembershipViewSet`.

## v0.9.3 - (2025-12-27)

### Added
- **Billing**: Migration verified to `dj-stripe` 2.10.3 for robust payment handling.
- **Webhooks**: Refactored `billing/webhooks.py` to use `dj-stripe` signals (`webhook_post_process`).
- **Models**: Added foreign key link between `billing.Subscription` and `djstripe.Subscription`.

### Changed
- **Testing**: Achieved 100% test pass rate (47 tests).
- **Docs**: Updated README.md to reflect verified system status.

## v0.9.1-mk2 (2025-12-27)

### Agregado
- **Aumento de Cobertura de Tests**: Se añadieron tests unitarios e integración para áreas críticas.
    - `tests/test_billing_webhooks.py`: Cobertura completa de webhooks de Stripe (Checkout, Suscripciones, Facturas).
    - `tests/test_multitenant_middleware.py`: Validación de la resolución de tenants por dominio y headers.
- **Correcciones**: Fix de compatibilidad `django.utils.timezone` en `src/billing/webhooks.py`.
- **Estado**: 45/45 tests pasando (100%).

## [0.9.1-mk1] - 2025-12-27

### Corregido
- **Tests Obsoletos Eliminados**: Se eliminaron `tests/test_onboarding_extended.py` y `tests/test_frontend_views.py` que probaban vistas de Django Template reemplazadas por Next.js.
- **Estabilidad**: Suite de tests pasando al 100% (35/35 tests).

## [0.9.1] - 2025-12-27

### Agregado
- **AGENTS.md Estándar**: Documento principal para agentes AI siguiendo [agent.md](https://agent.md)
  - Sistema de diseño dual documentado (Glass/Dark + Clean/Minimal)
  - Principios arquitectónicos: Stateless, PWA OfflineFirst, Secure by Default
- **PWA OfflineFirst**: Almacenamiento local encriptado
  - `frontend/src/lib/storage.ts`: Clase `OfflineStorage` con Dexie + crypto-js (AES)
  - Dependencias: `dexie@4.2.1`, `crypto-js@4.2.0`
- **Sistema de Diseño Glass UI**:
  - `frontend/src/components/ui/glass/GlassCard.tsx`: Tarjetas con glassmorphism
  - `frontend/src/components/ui/glass/GlassButton.tsx`: Botones con efecto neon
  - `frontend/src/components/ui/glass/GlassModal.tsx`: Modales con backdrop blur
  - `frontend/tailwind.config.ts`: Tokens personalizados (shadow-glass, shadow-neon)
- **Configuración Docker flexible**:
  - Puertos configurables vía `.env` (FRONTEND_PORT, DJANGO_PORT, POSTGRES_PORT, REDIS_PORT)
  - Rango 9xxx por defecto para evitar conflictos

### Cambiado
- **Backend Security Refactor**:
  - `src/config/settings/dev.py`: CORS/CSRF origins ahora usan `env.list()` en lugar de listas hardcodeadas
  - `src/core/management/commands/seed_demo.py`: Dominios dinámicos desde `ALLOWED_HOSTS`
- **Frontend Dockerfile**: Cambiado `npm ci` → `npm install --legacy-peer-deps` para mayor tolerancia
- **docker-compose.yml**: Todos los puertos usan variables de entorno con defaults seguros

### Corregido
- Sincronización de `package-lock.json` (89 paquetes agregados)
- Conflictos de puertos con otros proyectos Docker (mayordomos, rag-google)
- Migraciones de base de datos aplicadas (`axes.0010_accessattemptexpiration`)

### Estado del Sistema
- **Frontend**: http://localhost:9000 (Next.js 16.0.10)
- **Backend API**: http://localhost:9001 (Django 5.x)
- **PostgreSQL**: localhost:9432
- **Redis**: localhost:9379
- **MinIO**: localhost:9002 (Console), 9003 (API)
- **Mailpit**: localhost:8025

### Credenciales de Desarrollo
- Email: `admin@demo.com`
- Password: `password`

## [0.9.1-pre] - 2025-12-13

### Agregado
- Runbook de migración HTMX → React + Next.js (`docs/runbooks/migracion-frontend-nextjs.md`)
- ADR 0013 para roadmap de frontend (`docs/adr/0013-frontend-nextjs.md`)
- Endpoint `GET /api/v1/csrf/` para CSRF token (SessionAuth desde React)
- Endpoint `POST /api/v1/memberships/invite/` (invitar miembros por email)
- `GET /api/v1/tenant/` incluye `branding` y `domain_base`
- OpenAPI auth scheme para `ApiKeyAuthentication`

### Cambiado
- `ApiKeyAuthentication` valida pertenencia del API key al tenant del request
- `seed_demo` asegura dominios `localhost` y `127.0.0.1` para el tenant demo
- Generación de `username` desde email en onboarding/invites para evitar colisiones
- `.gitignore` incluye artefactos de Next.js (`.next/`, `out/`, `.turbo/`)

## [0.9.0] - 2025-12-13

### Agregado
- Comando `seed_demo` para inicializar entorno de demostración completo
- Páginas de autenticación estilizadas con Tailwind CSS (login/signup)
- Mejoras en manejo de sesiones y autenticación
- Documentación completa en `RESUMEN_PROYECTO.md` y `REPORTE_DESARROLLO.md`
- Health checks: `/healthz`, `/readyz`, `/metrics`

### Cambiado
- Django fijado a `>=5.0,<6.0` (actualmente 5.2.9)
- `seed_rbac` ahora itera sobre todos los tenants y hace schema switching correcto
- Estructura del proyecto limpiada (eliminados archivos obsoletos)
- Docker Compose estabilizado con puerto 7777 para desarrollo
- Configuración de CSP migrada a formato `django-csp==4.x`

### Corregido
- Import de rate-limit en `src/oauth/views.py`
- Error `admin.E013` en `core.admin.RoleAdmin` usando inline
- `ROOT_DIR` corregido para rutas estáticas en contenedor
- Middleware de Allauth agregado (`AccountMiddleware`)
- Build de Docker dev corrigiendo copia de requirements

### Estado
- Sistema funcional y estable
- Docker operativo con todos los servicios
- Multitenancy en modo schema funcionando
- Módulos V1 operativos: core, multitenant, billing, api, oauth
- Tests: 14 pasando, 6 fallando (cobertura 58.57%, objetivo 90%)

## [0.6.0-source-of-truth-protocol] - Pre-release

### Nota
Versión de protocolo de source of truth.

## [0.5.0] - Pre-release

### Nota
Versión pre-release con funcionalidades base.

## [0.1.1] - Pre-release

### Nota
Versión inicial con estructura base.

## [0.1.0] - Pre-release

### Nota
Versión inicial del proyecto.

[0.9.0]: https://github.com/untalcamilomedina/proyecto-semilla/releases/tag/v0.9.0
[0.9.1]: https://github.com/untalcamilomedina/proyecto-semilla/releases/tag/v0.9.1
[0.6.0-source-of-truth-protocol]: https://github.com/untalcamilomedina/proyecto-semilla/releases/tag/v0.6.0-source-of-truth-protocol
[0.5.0]: https://github.com/untalcamilomedina/proyecto-semilla/releases/tag/v0.5.0
[0.1.1]: https://github.com/untalcamilomedina/proyecto-semilla/releases/tag/v0.1.1
[0.1.0]: https://github.com/untalcamilomedina/proyecto-semilla/releases/tag/v0.1.0
