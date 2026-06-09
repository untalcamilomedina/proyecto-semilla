# 🌱 Proyecto Semilla

[![Version](https://img.shields.io/badge/version-0.14.0-blue.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.x-green.svg)](https://www.djangoproject.com/)
[![Next.js](https://img.shields.io/badge/next.js-16-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Boilerplate SaaS multitenant, seguro y AI-first.** La base para construir productos
SaaS en días, no meses: Django 5 + DRF + Next.js 16, multitenancy por schema de
Postgres, RBAC granular, billing con Stripe, observabilidad, CI/CD, despliegue
blue-green y un toolkit completo para desarrollar con agentes de IA.

## Tabla de contenidos

1. [Instalación en 3 pasos](#instalación-en-3-pasos)
2. [Qué incluye](#qué-incluye)
3. [Desarrollo AI-first](#desarrollo-ai-first)
4. [Arquitectura](#arquitectura)
5. [Seguridad](#seguridad)
6. [Comandos](#comandos)
7. [Variables de entorno](#variables-de-entorno)
8. [Deploy](#deploy)
9. [Estado del proyecto](#estado-del-proyecto)

## Instalación en 3 pasos

Requisitos: Docker + Docker Compose (y Python 3 para el wizard).

```bash
# 1. Clona y corre el wizard (nombre, módulos, claves únicas, env files)
git clone <tu-fork> mi-proyecto && cd mi-proyecto
make init        # o: python3 scripts/bootstrap.py --defaults

# 2. Levanta el stack completo
make dev   # web :8000 · frontend :3010 · postgres · redis · minio · mailpit

# 3. Migra y siembra datos demo (en otra terminal)
make migrate && make seed
```

Abre `http://localhost:3010` — login demo: `admin@demo.com` / `password`.
API interactiva en `http://localhost:8000/api/docs/`.

## Qué incluye

| Área | Implementación |
| --- | --- |
| **Multitenancy** | Schema-per-tenant en Postgres + RLS, resolución por dominio, aislamiento verificado por tests |
| **Auth** | JWT (con binding por tenant), API Keys por organización, sesión + allauth (Google OAuth), verificación de email |
| **RBAC** | Roles y permisos granulares estilo Discord, deny-by-default en todo el API |
| **Billing** | Stripe vía dj-stripe: checkout, portal, webhooks firmados e idempotentes, planes/precios/cuotas de uso |
| **API** | DRF versionada (`/api/v1/`) + OpenAPI (drf-spectacular), throttling, paginación |
| **Frontend** | Next.js 16 App Router, TypeScript estricto, Tailwind v4, design system "Glass" con Storybook, i18n (es/en/pt), TanStack Query + Zustand |
| **Onboarding** | Wizard completo: organización → módulos → plan → pago → invitaciones |
| **Módulos opcionales** | CMS (MDX), LMS, Community, MCP, CRM (empresas, contactos, pipeline de deals, actividades) — activables por feature flag |
| **Observabilidad** | Sentry, Prometheus `/metrics` (protegido), logs JSON, health checks (`/healthz`, `/readyz`, `/ht/`) |
| **Infra** | Docker multi-stage non-root, compose dev/prod, deploy blue-green con nginx, receta Fly.io |
| **Calidad** | CI (lint, mypy, tests con Postgres real, build, pip-audit/npm audit, Trivy), pre-commit, 110+ tests backend + vitest |

## Desarrollo AI-first

El seed está diseñado para construir software con agentes de IA desde el día uno:

- **`CLAUDE.md`** — guía del proyecto para agentes (arquitectura, reglas de seguridad, convenciones).
- **`.claude/skills/`** — 23 skills reutilizables: scaffolding full-stack, generación de tests, hardening, design system, i18n…
- **Hooks** (`.claude/settings.json`) — contexto automático al iniciar sesión y lint inmediato tras cada edición Python.
- **MCP** (`.mcp.json`) — servidor Postgres para que el agente inspeccione el schema en dev; módulo `mcp` opcional para exponer un catálogo de tools del API por tenant.
- **Workflow `@claude`** (`.github/workflows/claude.yml`) — menciona `@claude` en issues/PRs para que el agente trabaje en GitHub (requiere `ANTHROPIC_API_KEY`).

## Arquitectura

```
proyecto-semilla/
├── src/                    # Backend Django
│   ├── config/             # Settings por entorno (base/dev/prod/test)
│   ├── core/               # Usuarios, RBAC, onboarding
│   ├── multitenant/        # Schema-per-tenant + RLS + middleware
│   ├── billing/            # Stripe, planes, suscripciones, metering
│   ├── api/                # DRF v1 + auth (JWT/API Keys)
│   ├── common/             # Permisos, cifrado, métricas, helpers
│   ├── oauth/              # django-allauth
│   └── cms|lms|community|mcp|crm/  # Módulos opcionales
├── frontend/               # Next.js 16 (App Router + design system Glass)
├── compose/                # Docker Compose dev/prod + nginx + blue-green
├── deploy/flyio/           # Receta Fly.io
├── tests/                  # Suite backend (pytest + Postgres)
├── docs/                   # MkDocs: arquitectura, ADRs, runbooks, auditoría
└── .claude/                # Skills + hooks para agentes de IA
```

Detalles en [docs/architecture.md](docs/architecture.md) y los [ADRs](docs/adr/).

## Seguridad

Modelo completo en [SECURITY.md](SECURITY.md). Garantías clave, todas con tests
(`tests/test_api_security.py`):

- Ningún endpoint de tenant responde sin **membresía activa** en ese tenant.
- Un **JWT emitido en un tenant no autentica en otro** (claim de schema).
- Rate limiting en endpoints públicos (nginx + django-ratelimit + axes).
- Cifrado de campos sensibles con clave dedicada (`FIELD_ENCRYPTION_KEY`).
- Webhooks Stripe con firma, validación de metadata e idempotencia.
- `check --deploy` en CI; HSTS, cookies Secure y CSP en producción.

## Comandos

```bash
make dev              # stack Docker completo
make migrate          # migraciones schema public
make seed             # tenant demo + usuario + planes
make lint|fmt         # ruff, black, isort, djlint, bandit
make typecheck        # mypy
make test             # pytest (requiere Postgres — usar dentro de Docker)
make frontend-test    # eslint + tsc + vitest
make frontend-build   # build de producción Next.js
make audit            # pip-audit + safety

# Tenants
docker compose -f compose/docker-compose.yml exec web python manage.py create_tenant "Nombre" slug
docker compose -f compose/docker-compose.yml exec web python manage.py migrate_tenants
```

## Variables de entorno

Plantillas: [`local.env.example`](local.env.example) (dev) y
[`production.env.example`](production.env.example) (prod, con checklist de claves
dedicadas: `FIELD_ENCRYPTION_KEY`, `JWT_SIGNING_KEY`, `METRICS_TOKEN`).

## Deploy y operación

- **Stateless por diseño** (12-factor): estado en Postgres/Redis/S3, JWT sin
  estado de servidor, logs a stdout — escala horizontal sin fricción. Guía
  completa: [docs/runbooks/operacion.md](docs/runbooks/operacion.md).
- **Blue-green con nginx** (VPS/Docker): `compose/deploy.sh blue|green` — build del
  color inactivo, migraciones, health checks y switch de upstream sin downtime.
- **Fly.io**: receta en [`deploy/flyio/`](deploy/flyio/) (`make deploy`).
- **API documentada**: [docs/api.md](docs/api.md) + Swagger/Redoc generados del
  código. **MCP documentado**: [docs/mcp.md](docs/mcp.md).

## Estado del proyecto

`v0.14.0` — ver [CHANGELOG.md](CHANGELOG.md). Auditoría de seguridad completa y plan
de estabilización vigente en [`docs/auditoria/`](docs/auditoria/). Roadmap en
[ROADMAP.md](ROADMAP.md).

## Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md). Licencia [MIT](LICENSE).
