# Guía para Gemini CLI / Code Assist

**La guía canónica del proyecto está en [`AGENTS.md`](./AGENTS.md)** — léela
antes de tocar código. Misma guía, cualquier agente: el arnés de Proyecto
Semilla es agnóstico de modelo.

- Arquitectura y reglas de seguridad: `AGENTS.md` (y `CLAUDE.md`, equivalente).
- Procedimientos reutilizables: `.claude/skills/` (markdown plano).
- Tools ejecutables (lint, tests, docs, skills) vía MCP: registra
  `scripts/mcp/seed_server.py` como servidor stdio (config en `.mcp.json`).
- Verificación obligatoria antes de terminar: `make lint && make typecheck
  && make test` y `make frontend-test`.
