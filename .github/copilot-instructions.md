# Instrucciones para GitHub Copilot

**Lee `AGENTS.md` en la raíz del repo** — es la guía canónica para cualquier
agente de IA en Proyecto Semilla (arquitectura, comandos, convenciones).

Reglas no negociables (resumen):

1. Todo viewset multitenant exige membresía: `common.api.permissions.IsTenantMember`
   o `PolicyPermission`. NUNCA `IsAuthenticated` a secas en recursos de tenant.
2. Querysets siempre scopeados: `filter(organization=request_tenant(self.request))`.
3. Secretos solo por variables de entorno; campos sensibles con `EncryptedCharField`.
4. Antes de dar por terminado: `make lint && make typecheck && make test`
   (backend) y `make frontend-test` (frontend).
5. Idioma: comentarios y docs en español; identificadores de código en inglés.

Procedimientos paso a paso en `.claude/skills/` (markdown plano, válido para
cualquier agente). Tools ejecutables vía MCP: `scripts/mcp/seed_server.py`.
