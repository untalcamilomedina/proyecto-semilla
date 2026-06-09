# Roadmap — Proyecto Semilla

> Boilerplate SaaS multitenant, seguro y AI-first. Este roadmap cubre la SEMILLA,
> no productos derivados. El plan detallado de cada fase vive en
> [docs/auditoria/PLAN-ESTABILIZACION.md](docs/auditoria/PLAN-ESTABILIZACION.md).

## ✅ v0.14 — Estabilización y saneamiento (actual)

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

## v0.15 — Confianza verificable

- [ ] Suite de aislamiento multitenant ampliada (matriz endpoint × rol × tenant)
- [ ] Lock de dependencias Python (pip-tools/uv) + Renovate/Dependabot
- [ ] Cobertura backend ≥ 70% medida en CI (gate realista; hoy `fail_under=90` es aspiracional)
- [ ] E2E con Playwright: login, onboarding completo, invitación, upgrade de plan
- [ ] Migrar templates Django (allauth) a assets locales → CSP sin `unsafe-inline` ni CDNs

## v0.16 — Experiencia de adopción

- [ ] Script `scripts/bootstrap.py`: renombra proyecto, genera claves, configura branding en un paso
- [ ] Tokens de auth en cookies httpOnly + middleware SSR de protección de rutas
- [ ] Documentación de extensión: "cómo añadir un módulo" end-to-end con skill asociada
- [ ] Demo pública desplegada + capturas en README

## v1.0 — Producto vendible

- [ ] Versionado semántico estricto + releases firmados + CHANGELOG automatizado
- [ ] Guía de migración entre versiones del seed para proyectos derivados
- [ ] Plantilla de repositorio GitHub ("Use this template") + cookiecutter opcional
- [ ] Auditoría de seguridad externa
