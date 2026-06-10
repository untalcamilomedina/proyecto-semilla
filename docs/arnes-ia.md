# El Arnés de IA — desarrollo agnóstico de modelo

Proyecto Semilla está diseñado para que **cualquier agente de IA** (Claude,
Copilot, Cursor, Gemini, Codex, o el que exista mañana) pueda desarrollar y
mantener el sistema con la misma seguridad que un ingeniero senior. El arnés
no depende de ningún proveedor: se apoya en tres principios.

## Principios

1. **Contexto portable** — las reglas viven en archivos estándar del repo,
   no en la memoria de un modelo: `AGENTS.md` (canónico) replicado por
   puntero en cada ecosistema.
2. **Verbos ejecutables** — el agente no "cree" que terminó: ejecuta los
   mismos gates que el CI (lint, typecheck, tests) vía Make o MCP.
3. **Verificación independiente** — el guardrail final es el CI: tests de
   aislamiento multitenant, auditoría de dependencias y escaneo de imágenes
   bloquean cualquier regresión, la escriba un humano o una IA.

## Componentes

```
AGENTS.md / CLAUDE.md          ← contexto canónico (qué es esto, reglas, comandos)
.claude/skills/*/SKILL.md      ← 23 procedimientos paso a paso (markdown plano)
scripts/mcp/seed_server.py     ← tools MCP: status, lint, typecheck, tests,
                                  list_skills, read_skill, read_doc
.mcp.json                      ← registra "semilla" + "postgres-dev" (schema real)
scripts/ai/session-context.sh  ← hook de inicio: rama, estado, mapa de docs
scripts/ai/check-python.sh     ← hook post-edición: ruff inmediato
.github/workflows/ci.yml       ← guardrail: 7 gates obligatorios
.github/workflows/claude.yml   ← opcional: @claude en issues/PRs
```

## Conectar tu agente

| Herramienta | Cómo |
| --- | --- |
| **Claude Code** | Automático: lee `CLAUDE.md`, `.claude/skills/`, `.claude/settings.json` (hooks) y `.mcp.json` |
| **Cursor** | Automático: `.cursor/rules/proyecto-semilla.mdc`; añade el MCP en Settings → MCP con el comando de `.mcp.json` |
| **GitHub Copilot** | Automático: `.github/copilot-instructions.md`; MCP vía configuración de Copilot (VS Code `mcp.json`) |
| **Gemini CLI** | Lee `GEMINI.md`; registra el MCP en `~/.gemini/settings.json` con el comando de `.mcp.json` |
| **Codex / otros** | Estándar `AGENTS.md`; si soporta MCP, apunta a `scripts/mcp/seed_server.py` (stdio) |

El servidor MCP solo necesita Python 3 y el paquete `mcp`
(`pip install -r requirements/dev.txt`). Pruébalo:

```bash
python3 -c "
import asyncio, sys; sys.path.insert(0, 'scripts/mcp')
import seed_server
print([t.name for t in asyncio.run(seed_server.mcp.list_tools())])"
```

## El ciclo de trabajo del agente

1. **Orientarse** — `project_status` (MCP) o hook de sesión: rama, estado, docs.
2. **Buscar el procedimiento** — `list_skills` → `read_skill("scaffold-api-endpoint")`
   antes de inventar una solución.
3. **Implementar** siguiendo las reglas de `AGENTS.md` (membresía por tenant,
   scoping, secretos por env, i18n ×3).
4. **Verificarse** — `run_lint` + `run_typecheck` + `run_backend_tests` (+
   `run_frontend_tests` si tocó frontend). Sin verde no hay "terminado".
5. **Entregar** — PR con la plantilla; el CI repite los gates como árbitro.

## Por qué esto te independiza del modelo

- Si mañana cambias de Claude a otro agente, **no pierdes nada**: el contexto
  (AGENTS.md), los procedimientos (skills en markdown), los verbos (Make/MCP)
  y los guardrails (CI) son archivos del repo, no features de un proveedor.
- Las skills son texto plano versionado: cualquier LLM las lee; el
  `skill-generator` documenta cómo crear nuevas.
- MCP es un estándar abierto con SDKs en todos los ecosistemas; el servidor
  del seed son ~150 líneas de Python que puedes extender (añade un
  `@mcp.tool()` y listo).

## Extender el arnés

- **Nueva tool MCP**: función con docstring + `@mcp.tool()` en
  `scripts/mcp/seed_server.py` (la firma y el docstring SON la interfaz que
  ve el agente).
- **Nueva skill**: usa la skill `skill-generator`; guárdala en
  `.claude/skills/<nombre>/SKILL.md` y regístrala en el README del catálogo.
- **Nuevo guardrail**: añádelo a `ci.yml` — si no corre en CI, no protege.
