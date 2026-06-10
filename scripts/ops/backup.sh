#!/usr/bin/env bash
# Backup completo de Postgres (todos los schemas: public + tenants).
#
# Uso:   DATABASE_URL=postgresql://... scripts/ops/backup.sh [directorio_destino]
# Salida: <destino>/semilla-YYYYmmdd-HHMMSS.dump (formato custom de pg_dump)
#
# Programa esto a diario (cron/systemd timer) y sube el dump a almacenamiento
# externo (S3 con object-lock recomendado). Un backup que no se prueba con
# restore NO es un backup: ver el simulacro en scripts/ops/restore.sh.
set -euo pipefail

: "${DATABASE_URL:?Define DATABASE_URL (postgresql://user:pass@host:puerto/bd)}"
DEST_DIR="${1:-./backups}"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="${DEST_DIR}/semilla-${STAMP}.dump"

mkdir -p "${DEST_DIR}"
echo "→ pg_dump (formato custom, todos los schemas) → ${OUT}"
pg_dump --format=custom --no-owner --file="${OUT}" "${DATABASE_URL}"

SIZE=$(du -h "${OUT}" | cut -f1)
echo "✔ Backup completado (${SIZE})."
echo "  Restore de prueba: scripts/ops/restore.sh ${OUT} <DATABASE_URL_DE_PRUEBA>"
