#!/usr/bin/env bash
# Hook SessionStart de Claude Code: orienta al agente al iniciar sesión.
# Salida corta a stdout — se inyecta como contexto.
set -euo pipefail

cd "$(dirname "$0")/../.."

echo "── Proyecto Semilla · contexto de sesión ──"
echo "Rama: $(git branch --show-current 2>/dev/null || echo '?') · Último commit: $(git log -1 --format='%h %s' 2>/dev/null | cut -c1-72)"

if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
  echo "⚠ Working tree con cambios sin commitear ($(git status --porcelain | wc -l) archivos)."
fi

if command -v docker >/dev/null 2>&1 && docker compose -f compose/docker-compose.yml ps --status running 2>/dev/null | grep -q web; then
  echo "Docker: stack dev corriendo (web/frontend arriba)."
else
  echo "Docker: stack dev NO corriendo — 'make dev' para levantarlo. Los tests backend requieren Postgres."
fi

echo "Guía completa: CLAUDE.md · Skills: .claude/skills/ · Auditoría: docs/auditoria/"
