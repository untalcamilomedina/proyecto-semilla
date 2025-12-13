# Multitenancy (Schema Mode)

V1 usa multitenancy por **schemas de Postgres** con un `public` schema compartido y un schema por tenant.

## Modelo y dominios

- `multitenant.Tenant`: representa la organización/tenant. Campos clave:
  - `slug`: subdominio por defecto.
  - `schema_name`: nombre del schema (por defecto igual a `slug`).
- `multitenant.Domain`: mapea host → tenant (p.ej. `foo.acme.dev`).

Validaciones:

- Subdominios/schemas solo permiten `[a-z0-9-]` y no pueden ser reservados (`www`, `admin`, `api`, etc.).

## Resolución de tenant por host

El middleware `multitenant.middleware.TenantMiddleware`:

1. Lee `request.get_host()` y elimina el puerto.
2. Busca el host en `Domain`.
3. Asigna `request.tenant`.
4. Si hay tenant, ejecuta `SET search_path` al schema del tenant; si no, usa `public`.

## Cambio de schema

Helpers en `multitenant.schema`:

- `set_schema(schema)`: ajusta `search_path`.
- `schema_context(schema)`: context manager que cambia y restaura el schema.
- `create_schema(schema)`: crea el schema si no existe.

## Migraciones por schema

Comandos:

- `python manage.py create_tenant <name> <slug> [--schema] [--domain]`
  - Crea fila en `Tenant`, `Domain` principal y el schema.
- `python manage.py migrate_tenants [--schema=<schema>] [--skip-public]`
  - Ejecuta `migrate` primero en `public` y luego en cada schema activo.
- `python manage.py list_tenants`
  - Lista tenants y sus dominios.

Estrategia V1:

- Todas las apps actuales migran en cada schema (incluye `core`, `billing`, etc.).
- En V2 separaremos **shared apps vs tenant apps** para evitar duplicar tablas compartidas.

## Tests de regresión

Casos cubiertos en `tests/test_multitenant.py`:

- `create_tenant` crea schema y domain.
- Validación de subdominios reservados.
- `schema_context` cambia/restaura schema.
- Middleware resuelve `request.tenant` por host.

## Preset enterprise (database-per-tenant)

La opción `MULTITENANT_MODE=database` está preparada como flag, pero apagada en V1.
Se implementará un router por DB dedicada en un sprint futuro.

