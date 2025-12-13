# RBAC

## Modelos

- `Permission` (global)
- `Role` (por tenant)
- `Membership` (user+tenant+role)
- `RolePermission`

## Policies

Toda validación de acceso usa `common.policies.has_permission`.

## UI

Pantalla `/roles/` permite CRUD + export/import JSON con auditoría.

