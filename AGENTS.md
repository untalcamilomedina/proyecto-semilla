# AGENTS.md

> Configuración para agentes de IA en **Proyecto Semilla**.
> La guía canónica vive en [`CLAUDE.md`](./CLAUDE.md) — léela primero.

## Resumen

Este repositorio es un **boilerplate SaaS genérico** (Django 5 + DRF + Next.js 16) con
multitenancy por schema, RBAC, billing con Stripe y tooling AI-first. No contiene
lógica de producto: los productos se crean en repos derivados de esta semilla.

## Reglas principales

1. **Idioma:** comunicaciones, comentarios y documentación en **español**; identificadores de código en inglés.
2. **No suposiciones:** si falta información, pregunta o audita. Nunca inventes soluciones parche.
3. **Seguridad primero:** respeta las reglas no negociables de `CLAUDE.md` (membresía por tenant, scoping de querysets, rate limiting, secretos por env).
4. **Calidad:** `make lint && make typecheck && make test` (backend) y `make frontend-test` (frontend) deben pasar antes de dar por terminado un cambio.

## Recursos para agentes

| Recurso | Ubicación |
| --- | --- |
| Guía completa del proyecto | `CLAUDE.md` |
| Skills (23 capacidades reutilizables) | `.claude/skills/` |
| Hooks de sesión y lint | `.claude/settings.json` + `scripts/ai/` |
| Servidores MCP (Postgres dev) | `.mcp.json` |
| Workflow @claude en GitHub | `.github/workflows/claude.yml` |
| Auditoría y plan vigente | `docs/auditoria/` |
