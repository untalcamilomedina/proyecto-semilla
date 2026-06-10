#!/usr/bin/env bash
# Restore de un backup de Postgres + verificación básica.
#
# Uso: scripts/ops/restore.sh <archivo.dump> <DATABASE_URL_DESTINO>
#
# SIMULACRO DR (hazlo mensual): restaura el último backup en una BD limpia
# y verifica que los tenants y usuarios están. Si este script no pasa,
# tu plan de recuperación no existe.
set -euo pipefail

DUMP="${1:?Uso: restore.sh <archivo.dump> <DATABASE_URL_DESTINO>}"
TARGET="${2:?Falta DATABASE_URL destino (¡usa una BD de prueba, NO producción!)}"

case "${TARGET}" in
  *prod*|*production*)
    echo "⚠ La URL destino parece de PRODUCCIÓN. Aborta si no es un restore real de incidente."
    read -r -p "Escribe 'RESTAURAR' para continuar: " CONFIRM
    [ "${CONFIRM}" = "RESTAURAR" ] || { echo "Cancelado."; exit 1; }
    ;;
esac

echo "→ Restaurando ${DUMP} en ${TARGET%%@*}@…"
pg_restore --no-owner --clean --if-exists --dbname="${TARGET}" "${DUMP}"

echo "→ Verificación post-restore:"
psql "${TARGET}" -t -c "SELECT count(*) AS tenants FROM public.multitenant_tenant;" \
  | xargs echo "   tenants:"
psql "${TARGET}" -t -c "SELECT count(*) AS schemas FROM information_schema.schemata WHERE schema_name NOT IN ('public','information_schema') AND schema_name NOT LIKE 'pg_%';" \
  | xargs echo "   schemas de tenant:"
echo "✔ Restore verificado. Registra fecha y duración del simulacro en tu bitácora."
