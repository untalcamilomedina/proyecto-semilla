#!/usr/bin/env bash
# Hook PostToolUse (Edit/Write sobre *.py): feedback inmediato de lint para el agente.
# Lee el JSON del hook por stdin; sale 0 siempre (no bloquea), imprime avisos.
set -uo pipefail

payload="$(cat)"
file_path="$(printf '%s' "$payload" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null || true)"

case "$file_path" in
  *.py)
    if command -v ruff >/dev/null 2>&1; then
      ruff check --quiet "$file_path" 2>&1 | head -20 || true
    else
      python3 -m py_compile "$file_path" 2>&1 | head -5 || true
    fi
    ;;
esac
exit 0
