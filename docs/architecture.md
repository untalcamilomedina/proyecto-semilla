# Arquitectura
## Table of Contents
1. [Layout](#layout)
2. [Principios](#principios)
3. [Multitenancy](#multitenancy)
## Layout

El código vive en `src/`:

- `config/` — settings por entorno, urls, ASGI/WSGI.
- `common/` — utilidades compartidas, policies, middleware.
- `core/` — usuarios, organizaciones (Tenant), roles/permisos, onboarding.
- `multitenant/` — resolución por host y switching de schemas.
- `billing/` — Stripe, planes, suscripciones, webhooks.
- `api/` — DRF, versionado y OpenAPI.
- `oauth/` — allauth + hardening de login.

## Principios

- Lógica de negocio en servicios (no en views).
- Apps modulares y desacopladas; comunicación vía señales/capabilities.
- Políticas unificadas para UI HTMX y DRF.

## Multitenancy

Modo V1 `schema`:

- Tabla `Tenant` se replica a cada schema para soportar FKs.
- `public` contiene `Tenant`/`Domain` fuente de verdad para routing.
- Middleware resuelve host en `public`, cambia schema y expone `request.tenant`.

Detalles en `docs/multitenancy.md`.

