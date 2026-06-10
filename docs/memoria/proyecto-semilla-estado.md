---
title: Proyecto Semilla — Estado y conocimiento canónico
type: note
tags:
- proyecto-semilla
- boilerplate
- saas
- estado
permalink: proyecto-semilla/estado-canonico
---

# Proyecto Semilla — Estado y conocimiento canónico

> Nota en formato Basic Memory. Versionada en el repo (`docs/memoria/`) para que
> viaje con cada clone; impórtala a tu Basic Memory copiándola o apuntando la
> carpeta del proyecto de memoria aquí. Actualízala en cada release.

Boilerplate SaaS multitenant **seguro, stateless y AI-first** (Django 5 + DRF +
Next.js 16). Repo: `untalcamilomedina/proyecto-semilla`. Versión actual:
**v0.15.0** (`main`, tag pendiente de push por el mantenedor).

## Observations

- [estado] v0.15.0 en main con CI 7/7 verde y 126/126 tests backend (Postgres y Redis reales) #release
- [estado] Dos auditorías integrales ejecutadas y corregidas (2026-06): informe en docs/auditoria/2026-06-informe-auditoria.md #auditoria
- [arquitectura] Multitenancy schema-per-tenant en Postgres + RLS; tenant resuelto por dominio en TenantMiddleware (corre antes de auth) #multitenant
- [arquitectura] Techo de schema-per-tenant ~2K tenants; ruta a row-level documentada con disparadores medibles en ADR 0015 #escalado
- [arquitectura] Stateless 12-factor: datos en Postgres, sesiones cached_db, JWT sin estado, media en S3, logs JSON a stdout, Celery para async #stateless
- [seguridad] Deny-by-default: todo endpoint de tenant exige membresía activa (IsTenantMember/PolicyPermission) — ADR 0014 #rbac
- [seguridad] JWT con binding por schema (claim schema_name): un token de un tenant es rechazado en otro; sin esto había suplantación por colisión de IDs #jwt
- [seguridad] MFA TOTP + códigos de recuperación en /accounts/2fa/ (allauth.mfa); SSO SAML/OIDC definido como futuro módulo enterprise #mfa
- [seguridad] Claves dedicadas: DJANGO_SECRET_KEY, FIELD_ENCRYPTION_KEY (cifrado de campos), JWT_SIGNING_KEY, METRICS_TOKEN #secretos
- [seguridad] Webhooks Stripe: firma dj-stripe + metadata validada contra BD + idempotencia por StripeEvent.event_id #billing
- [seguridad] Todas las garantías están codificadas en tests/test_api_security.py y test_crm.py — el CI bloquea regresiones #tests
- [gdpr] export_user_data (acceso/portabilidad JSON cross-schema) y delete_user_data (anonimización irreversible); plazo 30 días en runbook #gdpr
- [observabilidad] X-Request-ID en cada respuesta; request_id + tenant inyectados en todos los logs JSON (common.request_context) #trazabilidad
- [observabilidad] OpenTelemetry opt-in vía OTEL_EXPORTER_OTLP_ENDPOINT (Tempo/Jaeger/Datadog); Sentry y Prometheus /metrics con token #otel
- [api] API REST versionada /api/v1/ documentada en docs/api.md + Swagger /api/docs/ + Redoc /api/redoc/ + make api-schema exporta openapi.yaml #api
- [api] Auth del API: JWT (15min access/7d refresh con rotación+blacklist), API Keys hasheadas por tenant (X-Api-Key), sesión+CSRF #auth
- [modulos] Núcleo: core, multitenant, billing (Stripe checkout/portal/metering), api, oauth, common. Opcionales por flag: cms, lms, community, mcp_registry, crm #modulos
- [modulos] CRM opcional: companies/contacts/deals(pipeline con cierre automático)/activities; lectura=miembro, escritura=crm.manage_crm #crm
- [arnes-ia] Servidor MCP propio scripts/mcp/seed_server.py con 8 tools: project_status, run_lint, run_typecheck, run_backend_tests, run_frontend_tests, list_skills, read_skill, read_doc #mcp
- [arnes-ia] Contexto portable: AGENTS.md canónico (= CLAUDE.md) + .cursor/rules/ + .github/copilot-instructions.md + GEMINI.md — agnóstico de modelo #agnostico
- [arnes-ia] 23 skills en .claude/skills/ (markdown plano, cualquier agente las lee; también vía MCP list_skills/read_skill) #skills
- [arnes-ia] Hooks: scripts/ai/session-context.sh (orientación al abrir sesión) y check-python.sh (ruff tras cada edición) #hooks
- [arnes-ia] La app Django del registro MCP por tenant se llama mcp_registry (label "mcp") para no eclipsar al SDK oficial `mcp` #naming
- [dx] Instalación en 3 pasos: make init (wizard 4 pasos estilo WordPress/Mautic/cal.com: requisitos, proyecto, módulos, resumen+confirmación, genera 3 claves únicas y env files) → make dev → make migrate && make seed #wizard
- [dx] Demo: admin@demo.com/password en localhost:3010; API docs en localhost:8000/api/docs/ #demo
- [dx] Quien clona el seed queda listo para continuar con IA: Claude Code lee CLAUDE.md/skills/hooks/.mcp.json automáticamente; Cursor/Copilot/Gemini vía sus punteros; el flujo es orientarse→skill→implementar→verificarse con los gates #ia-ready
- [calidad] Gates: make lint (ruff+black+isort+djlint+bandit), make typecheck (mypy), make test (pytest, requiere Postgres), make frontend-test; CI además pip-audit, npm audit, Trivy, deploy-smoke, docker-build #ci
- [operacion] Blue-green con nginx (compose/deploy.sh), backup/restore con verificación (scripts/ops/), k6 línea base (make load-test, p95<500ms), runbook docs/runbooks/operacion.md #operacion
- [gobernanza] Issue forms, PR template con gates, CODEOWNERS rutas sensibles, Dependabot semanal pip/npm/actions, Release automático en tags v*, CONTRIBUTING #gobernanza
- [decision] django-waffle eliminado (cero usos): los flags reales son ENABLE_* por env + Tenant.enabled_modules por tenant #decision
- [decision] Celery hecho real: emails async con patrón tenant-aware (task recibe schema_name y usa schema_context — plantilla en core/tasks.py); eager en DEBUG/tests #decision
- [historia] El repo mezclaba un producto (AppNotion: Notion/Miro/IA) y 5 marcas; se extirpó en v0.14 y el seed volvió a ser genérico #historia
- [bug-resuelto] config/__init__.py no cargaba la app Celery: cualquier .delay() desde el web usaba un broker amqp fantasma — corregido en v0.15 #bug
- [roadmap] v0.16: lock uv, matriz aislamiento ampliada, cobertura desde 70% medido, Playwright E2E, CSP estricta, cookies httpOnly; v1.0: releases firmados, template repo, auditoría externa #roadmap
- [pendiente] Tag v0.15.0 por publicar (la sesión remota no puede pushear tags): git tag -a v0.15.0 -m "..." && git push origin v0.15.0 #pendiente

## Relations

- documenta [[Proyecto Semilla]]
- detalla_api [[docs/api.md]]
- detalla_mcp [[docs/mcp.md]]
- detalla_arnes [[docs/arnes-ia.md]]
- decision_aislamiento [[docs/adr/0014-aislamiento-deny-by-default.md]]
- decision_escalado [[docs/adr/0015-escalado-row-level.md]]
- plan_vigente [[docs/auditoria/PLAN-ESTABILIZACION.md]]
- guia_agentes [[AGENTS.md]]
- runbook [[docs/runbooks/operacion.md]]
