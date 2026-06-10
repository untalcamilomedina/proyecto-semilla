# AGENTS.md — Guía canónica para agentes de IA

> Proyecto Semilla: boilerplate SaaS multitenant (Django 5 + DRF + Next.js 16), seguro y AI-first.
> Esta guía es **agnóstica de modelo**: vale para Claude, Copilot, Cursor, Gemini, Codex o
> cualquier agente. `CLAUDE.md` contiene la misma guía (se mantienen en sincronía).
> Idioma del proyecto: **español** (comentarios, docs, commits); identificadores de código en inglés.

## Arquitectura en 60 segundos

- **Backend** `src/`: Django 5 con settings por entorno en `src/config/settings/{base,dev,prod,test}.py`.
  - Apps núcleo: `core` (usuarios, RBAC, onboarding), `multitenant` (schema-per-tenant + RLS), `billing` (Stripe/dj-stripe), `api` (DRF v1), `oauth` (allauth + MFA), `common` (cifrado, permisos, métricas, request-context).
  - Apps opcionales por feature flag (`ENABLE_LMS`, `ENABLE_COMMUNITY`, `ENABLE_MCP`, `ENABLE_CRM` en env): `cms`, `lms`, `community`, `mcp`, `crm`.
- **Frontend** `frontend/`: Next.js App Router + TypeScript estricto + Tailwind v4 + design system "Glass" (`src/components/ui/glass/`). i18n con next-intl (`messages/{es,en,pt}.json` — es es el default). Estado: Zustand + TanStack Query.
- **Multitenancy**: `multitenant.middleware.TenantMiddleware` resuelve el tenant por dominio y fija el schema de Postgres. Corre ANTES de la autenticación: nunca dependas de `request.user` ahí. Techo y ruta de escalado: `docs/adr/0015-escalado-row-level.md`.
- **API**: `/api/v1/` (router en `src/api/v1/urls.py`). Auth: JWT con binding por tenant + API Keys (`X-Api-Key`) + sesión. Docs: `docs/api.md`.
- **Tareas async**: Celery con patrón tenant-aware — toda task recibe `schema_name` y usa `schema_context` (ejemplo: `src/core/tasks.py`). En DEBUG/tests corren inline (`CELERY_TASK_ALWAYS_EAGER`).

## Reglas de seguridad NO negociables

1. **Todo viewset multitenant exige membresía**: usa `common.api.permissions.IsTenantMember` o `PolicyPermission` (valida membresía y, opcionalmente, `permission_codename`). NUNCA `IsAuthenticated` a secas en recursos de tenant. (ADR 0014)
2. **Scoping por tenant en queryset**: `Model.objects.filter(organization=request_tenant(self.request))` — helper en `common.api.tenancy`.
3. Endpoints públicos (signup/login/onboarding start) llevan `@ratelimit` y validadores de Django (`validate_password`).
4. Secretos SOLO por env (`environs`). Campos sensibles en BD → `common.encryption.EncryptedCharField` (clave: `FIELD_ENCRYPTION_KEY`).
5. Webhooks: valida metadata contra la BD (ver `billing/webhooks.py::_resolve_tenant`) e idempotencia con `StripeEvent`.

## Comandos (los mismos gates que el CI)

```bash
make init         # wizard de instalación (env files + claves)
make dev          # stack Docker (web :8000, frontend :3010, postgres, redis, minio, mailpit)
make migrate && make seed
make lint         # ruff + black + isort + djlint + bandit
make typecheck    # mypy
make test         # pytest (REQUIERE Postgres: dentro de Docker o con servicios arriba)
make frontend-test  # eslint + tsc + vitest
```

**Cierre de tarea**: nada está terminado hasta que los gates anteriores pasen.
Estos mismos comandos están disponibles como tools MCP (`scripts/mcp/seed_server.py`).

## Convenciones

- Migrations: nunca edites una migración commiteada; crea una nueva. Modelo cambiado ⇒ migración en el mismo PR.
- Serializers DRF: lista explícita de `fields` (nunca `__all__` en modelos con datos sensibles).
- Frontend: design system en `src/components/ui/glass/`; tokens semánticos, nunca colores hardcodeados. Branding en `src/lib/branding.ts`.
- i18n: toda string visible pasa por `useTranslations`; añade la clave a `messages/{es,en,pt}.json` (los tres).
- API del frontend: SIEMPRE rutas relativas `/api/v1/...` vía `src/lib/api.ts`.
- No tocar `frontend/src/types/api.ts` a mano (generado). No añadir lógica de producto al seed.
- No desactivar checks de CI; arregla la causa.

## El arnés (componentes, todos agnósticos)

| Pieza | Ubicación | Qué da |
| --- | --- | --- |
| Esta guía | `AGENTS.md` (= `CLAUDE.md`) | Contexto y reglas |
| Skills (23) | `.claude/skills/*/SKILL.md` | Procedimientos paso a paso (markdown plano) |
| MCP del seed | `scripts/mcp/seed_server.py` + `.mcp.json` | Tools: lint/typecheck/tests/skills/docs/status |
| MCP Postgres dev | `.mcp.json` | Inspección del schema real |
| Hooks | `scripts/ai/*.sh` (+ `.claude/settings.json`) | Contexto de sesión y lint inmediato |
| Punteros por herramienta | `.github/copilot-instructions.md`, `GEMINI.md`, `.cursor/rules/` | Mismo contexto en cada ecosistema |
| Workflow @claude | `.github/workflows/claude.yml` | Integración opcional en GitHub |
| Guardrail final | `.github/workflows/ci.yml` | Lo que no pasa el CI, no entra |

Documento completo del arnés: `docs/arnes-ia.md`.

## Mapa de documentación

- `README.md` — instalación en 3 pasos · `docs/api.md` — API · `docs/mcp.md` — MCP
- `docs/runbooks/operacion.md` — stateless, escalado, DR, GDPR
- `docs/auditoria/` — auditoría y plan vigente · `docs/adr/` — decisiones
