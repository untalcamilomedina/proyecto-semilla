# ADR 0015 — Techo de schema-per-tenant y ruta de migración a row-level

**Estado:** aceptado (decisión: NO migrar todavía) · **Fecha:** 2026-06

## Contexto

El seed usa **schema-per-tenant** en Postgres: aislamiento físico fuerte,
backups/borrado por tenant triviales, y RLS como segunda capa. Su techo
práctico: con miles de schemas, las migraciones son O(n·tablas) (un
`migrate_tenants` puede tardar horas con >2–3K tenants), el catálogo de
Postgres crece (planificación más lenta, `pg_dump` pesado) y el pooling por
schema se complica.

## ¿Qué implicaría migrar a row-level (single-schema) HOY?

Menos de lo habitual, porque el seed ya está medio preparado:

| Pieza | Estado actual | Trabajo para row-level |
| --- | --- | --- |
| FK `organization` en todos los modelos | ✅ ya existe en todos los módulos | Ninguno |
| Políticas RLS + `set_tenant_id()` | ✅ implementadas (`common/rls.py`) | Pasarían de defensa-en-profundidad a frontera principal |
| Scoping en querysets/permisos | ✅ deny-by-default por `organization` | Ninguno |
| `TenantMiddleware` | Cambia `search_path` | Solo fijaría `tenant_id` (quitar `set_schema`) |
| **Usuarios por schema** | ❌ el escollo real | Unificar usuarios en tabla global: migración de datos con resolución de colisiones de email entre tenants, re-emisión de tokens, rehacer el claim `schema_name` por `tenant_id` |
| Datos existentes | N schemas | Script de consolidación schema→public por tenant (downtime o doble-escritura) |

Estimación honesta: **2–3 semanas** de trabajo enfocado + ventana de migración,
con el 80 % del riesgo concentrado en la unificación de usuarios.

## Decisión

**No migrar ahora.** Schema-per-tenant es la elección correcta para el rango
0→2.000 tenants en que vivirá cualquier producto derivado durante años, y su
aislamiento es un argumento de venta enterprise. En su lugar:

1. Mantener el FK `organization` + RLS en TODO modelo nuevo (ya es regla),
   de modo que la puerta a row-level siga abierta sin reescrituras.
2. Disparadores para ejecutar esta migración (revisar trimestralmente):
   - `migrate_tenants` > 30 min en producción, o
   - > 2.000 tenants activos, o
   - necesidad de analítica cross-tenant en caliente.
3. Cuando se dispare: ejecutar la consolidación de usuarios primero (tabla
   global + `tenant_id` en claims), después el data-move por lotes.

## Consecuencias

- Cero coste hoy; ruta de escape documentada y barata gracias a las reglas 1.
- El módulo `MULTITENANT_MODE=database` del settings queda reservado para esa
  fase (hoy solo `schema`/`off` están soportados de verdad).
