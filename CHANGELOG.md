# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [0.9.1] - 2025-12-13

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
