# CLAUDE.md — Guía para agentes de IA

> Proyecto Semilla: boilerplate SaaS multitenant (Django 5 + DRF + Next.js 16), seguro y AI-first.
> Idioma del proyecto: **español** (comentarios, docs, commits descriptivos); identificadores de código en inglés.

## Arquitectura en 60 segundos

- **Backend** `src/`: Django 5 con settings por entorno en `src/config/settings/{base,dev,prod,test}.py`.
  - Apps núcleo: `core` (usuarios, RBAC, onboarding), `multitenant` (schema-per-tenant + RLS), `billing` (Stripe/dj-stripe), `api` (DRF v1), `oauth` (allauth), `common` (cifrado, permisos, métricas).
  - Apps opcionales por feature flag (`ENABLE_LMS`, `ENABLE_COMMUNITY`, `ENABLE_MCP`, `ENABLE_CRM` en env): `cms`, `lms`, `community`, `mcp`, `crm`.
- **Frontend** `frontend/`: Next.js App Router + TypeScript estricto + Tailwind v4 + design system "Glass" (`src/components/ui/glass/`). i18n con next-intl (`messages/{es,en,pt}.json` — es es el default). Estado: Zustand + TanStack Query.
- **Multitenancy**: `multitenant.middleware.TenantMiddleware` resuelve el tenant por dominio y fija el schema de Postgres. El middleware corre ANTES de la autenticación: nunca dependas de `request.user` ahí.
- **API**: `/api/v1/` (router en `src/api/v1/urls.py`). Auth: JWT (SimpleJWT) + API Keys (`X-Api-Key`) + sesión.

## Reglas de seguridad NO negociables

1. **Todo viewset multitenant exige membresía**: usa `common.api.permissions.IsTenantMember` o `PolicyPermission` (que ya valida membresía y, opcionalmente, `permission_codename`). NUNCA uses `IsAuthenticated` a secas en recursos de tenant.
2. **Scoping por tenant en queryset**: `Model.objects.filter(organization=request_tenant(self.request))` — helper en `common.api.tenancy`.
3. Endpoints públicos (signup/login/onboarding start) llevan `@ratelimit` y validadores de Django (`validate_password`).
4. Secretos SOLO por env (`environs`). Campos sensibles en BD → `common.encryption.EncryptedCharField` (clave: `FIELD_ENCRYPTION_KEY`).
5. Webhooks: valida metadata contra la BD (ver `billing/webhooks.py::_resolve_tenant`) e idempotencia con `StripeEvent`.

## Comandos

```bash
make dev          # levantar stack Docker (web :8000, frontend :3010, postgres, redis, minio, mailpit)
make migrate      # migraciones schema public
make seed         # datos demo
make lint         # ruff + black + isort + djlint + bandit
make typecheck    # mypy
make test         # pytest (REQUIERE Postgres: correr dentro de Docker o con servicios arriba)
cd frontend && npm run dev|build|lint|type-check|test
```

- Tests backend: `docker compose -f compose/docker-compose.yml exec web pytest tests/` (no soportan SQLite).
- Regenerar tipos del API en frontend: `cd frontend && npm run generate-sdk` (backend corriendo).

## Convenciones

- Migrations: nunca edites una migración ya commiteada; crea una nueva.
- Serializers DRF: lista explícita de `fields` (nunca `__all__` en modelos con datos sensibles).
- Frontend: componentes del design system en `src/components/ui/glass/`; usa tokens semánticos (`bg-primary`, `text-foreground`), nunca colores hardcodeados. Branding centralizado en `src/lib/branding.ts` (no hardcodear nombre/URLs).
- i18n: toda string visible pasa por `useTranslations`; añade la clave a `messages/{es,en,pt}.json` (los tres).
- Llamadas API del frontend: SIEMPRE rutas relativas `/api/v1/...` vía `src/lib/api.ts` (proxy a Django por rewrite en dev y por nginx en prod).

## Skills disponibles

Catálogo en `.claude/skills/` (23 skills): scaffolding full-stack, generación de tests, hardening, design system, i18n, etc. Úsalas cuando la tarea encaje — p.ej. `scaffold-api-endpoint` antes de crear un endpoint a mano.

## Qué NO hacer

- No añadir lógica de producto al seed: este repo es la base genérica. Los productos se construyen en repos derivados.
- No introducir dependencias sin actualizar `requirements/*.txt` (backend) o `package.json` + lockfile (frontend).
- No tocar `frontend/src/types/api.ts` a mano (generado por openapi-typescript).
- No desactivar checks de CI para que pase; arregla la causa.

## Mapa de documentación

- `README.md` — instalación en 3 pasos y visión general.
- `docs/auditoria/` — informe de auditoría y plan de estabilización vigente.
- `docs/adr/` — decisiones de arquitectura.
- `docs/runbooks/` — operaciones (local, fly.io, blue-green).
- `AGENTS.md` — apunta aquí (compatibilidad con otros agentes).
