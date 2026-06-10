# Roadmap — Proyecto Semilla

> Boilerplate SaaS multitenant, seguro y AI-first. Este roadmap cubre la SEMILLA,
> no productos derivados. El plan detallado de cada fase vive en
> [docs/auditoria/PLAN-ESTABILIZACION.md](docs/auditoria/PLAN-ESTABILIZACION.md).

## ✅ v0.14 — Estabilización y saneamiento

- [x] Extirpado el código de producto (integraciones Notion/Miro/IA) que se mezcló en el seed
- [x] Marca unificada: Proyecto Semilla (configurable vía `PROJECT_NAME` / `frontend/src/lib/branding.ts`)
- [x] Hardening crítico: membresía obligatoria por tenant, JWT con binding de schema,
      logout con blacklist, signup con validadores + rate limit, `/metrics` protegido,
      webhooks validados e idempotentes, claves dedicadas (cifrado/JWT)
- [x] Frontend real: rutas API corregidas (proxy en dev), billing conectado a Stripe
      checkout/portal, catálogo i18n completo (es/en/pt), datos fake eliminados
- [x] Build estable: lockfile npm limpio (sin `--legacy-peer-deps`), Storybook 10,
      Dockerfile frontend con stage de producción, límites de recursos en compose
- [x] CI reforzado: `check --deploy`, pip-audit/npm audit, Trivy, tests frontend
- [x] Toolkit AI-first: CLAUDE.md, 23 skills en `.claude/`, hooks, `.mcp.json`, workflow `@claude`

## ✅ v0.15 — Talla mundial: confianza y arnés agnóstico (actual)

- [x] MFA/2FA (TOTP + códigos de recuperación) — SSO SAML/OIDC definido como módulo enterprise
- [x] GDPR: export y anonimización cross-schema con tests (`export_user_data`/`delete_user_data`)
- [x] Trazabilidad: X-Request-ID + tenant en todos los logs; OpenTelemetry opt-in
- [x] Gobernanza completa: issue forms, PR template, CODEOWNERS, Dependabot, releases en tags
- [x] Arnés de IA agnóstico: MCP propio (8 tools = gates del CI), AGENTS.md canónico, punteros Cursor/Copilot/Gemini
- [x] Operación: k6 línea base, backup/restore con simulacro DR, runbook GDPR
- [x] Celery real (emails async tenant-aware); waffle eliminado (flags reales: env + `Tenant.enabled_modules`)
- [x] Wizard de instalación guiada (4 pasos, estilo WordPress/Mautic/cal.com)

## v0.16 — Confianza verificable

- [ ] Lock de dependencias Python (uv) — Dependabot ya activo
- [ ] Matriz de aislamiento ampliada (endpoint × rol × tenant, módulos opcionales incluidos)
- [ ] Subir cobertura backend gradualmente desde el 70% medido
- [ ] E2E con Playwright: login, onboarding completo, invitación, upgrade de plan
- [ ] Migrar templates Django (allauth) a assets locales → CSP sin `unsafe-inline` ni CDNs
- [ ] Tokens de auth en cookies httpOnly + middleware SSR de protección de rutas

## v0.17 — Experiencia de adopción

- [ ] Documentación de extensión: "cómo añadir un módulo" end-to-end con skill asociada
- [ ] Demo pública desplegada + capturas en README

## v1.0 — Producto vendible

- [ ] Versionado semántico estricto + releases firmados + CHANGELOG automatizado
- [ ] Guía de migración entre versiones del seed para proyectos derivados
- [ ] Plantilla de repositorio GitHub ("Use this template") + cookiecutter opcional
- [ ] Auditoría de seguridad externa
