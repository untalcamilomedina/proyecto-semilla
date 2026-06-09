# MCP — Model Context Protocol en Proyecto Semilla

El seed integra MCP en dos planos: **para desarrollar** (agentes que trabajan en
el código) y **para operar** (registro de servidores MCP por tenant + catálogo
de tools del API).

## 1. MCP para desarrollo (`.mcp.json`)

Al abrir el repo con Claude Code (u otro cliente MCP), `.mcp.json` configura:

```json
{
  "mcpServers": {
    "postgres-dev": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres",
               "postgresql://postgres:postgres@localhost:5432/proyecto_semilla"]
    }
  }
}
```

Esto permite al agente **inspeccionar el schema real de la BD de desarrollo**
(tablas, columnas, relaciones) sin adivinar. Añade aquí los servidores que tu
flujo necesite (filesystem, GitHub, etc.). Las credenciales son las del
Postgres de dev del compose — nunca apuntes este archivo a producción.

Complementos del arnés de desarrollo:

| Pieza | Archivo | Qué hace |
| --- | --- | --- |
| Guía del agente | `CLAUDE.md` | Arquitectura, reglas de seguridad, comandos |
| Skills (23) | `.claude/skills/` | Scaffolding, tests, hardening, design system |
| Hook SessionStart | `scripts/ai/session-context.sh` | Inyecta rama/estado/docs al iniciar |
| Hook PostToolUse | `scripts/ai/check-python.sh` | ruff inmediato tras editar .py |
| @claude en GitHub | `.github/workflows/claude.yml` | El agente atiende issues/PRs |

## 2. Módulo `mcp` (opcional, `ENABLE_MCP=true`)

App Django multitenant para que **cada organización registre y gobierne sus
propios servidores MCP** y para exponer el API del seed como catálogo de tools.

### Modelos

- **McpServer** — servidor MCP externo/interno del tenant: `name`,
  `endpoint_url`, credencial cifrada en BD (`EncryptedCharField` con
  `FIELD_ENCRYPTION_KEY`), `is_active`.
- **McpTool** — tools declaradas por servidor: `name`, `description`,
  `input_schema` (JSON Schema).
- **McpResource** — recursos expuestos (URIs/documentos).
- **McpUsageLog** — auditoría de invocaciones (server, tool, usuario, payload).

### Endpoints (`/api/v1/mcp/`)

| Método | Ruta | Descripción |
| --- | --- | --- |
| CRUD | `servers/`, `tools/`, `resources/`, `usage-logs/` | Registro por tenant (exige membresía) |
| GET | `catalog/` | **Catálogo de tools del API en formato MCP** |

`GET /api/v1/mcp/catalog/` introspecciona el router DRF y devuelve las
capacidades del API como definiciones de tools que un agente puede consumir:

```json
{
  "tools": [
    {"name": "memberships_list", "description": "...", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "crm_deals_create", "description": "...", "inputSchema": {"...": "..."}}
  ],
  "count": 42,
  "version": "1.0"
}
```

Seguridad: todos los endpoints exigen **membresía en el tenant**; las
credenciales de servidores nunca se devuelven en claro (cifradas at-rest).

### Conectar un agente al API del seed

Para que un agente opere TU SaaS (no el código), el patrón soportado:

1. Crea una **API Key** del tenant (`POST /api/v1/api-keys/`).
2. El agente consume `GET /api/v1/mcp/catalog/` para descubrir capacidades.
3. Invoca los endpoints REST con `X-Api-Key` (la key respeta RBAC y tenant).
4. Registra servidores MCP externos del tenant en `servers/` para orquestarlos.

> Roadmap (ver `docs/auditoria/PLAN-ESTABILIZACION.md`): scopes de API Key
> aplicados por endpoint y bridge MCP-protocolo nativo sobre el catálogo.
