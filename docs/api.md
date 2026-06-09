# API — Guía completa

API REST versionada bajo `/api/v1/`, construida con DRF + drf-spectacular.

## Documentación interactiva (OpenAPI)

| Recurso | URL |
| --- | --- |
| Swagger UI | `GET /api/docs/` |
| Redoc | `GET /api/redoc/` |
| Esquema OpenAPI (JSON/YAML) | `GET /api/schema/` |
| Exportar a archivo | `make api-schema` → `openapi.yaml` |
| Tipos TypeScript del frontend | `cd frontend && npm run generate-sdk` |

> El esquema se genera del código: cada viewset/serializer nuevo aparece
> automáticamente. Usa la skill `enrich-openapi-schema` para añadir ejemplos
> y descripciones con `@extend_schema`.

## Autenticación

El API acepta tres mecanismos (en este orden de prioridad):

### 1. JWT (recomendado para frontends y móviles)

```bash
# Obtener par de tokens (en el dominio del tenant)
curl -X POST https://demo.tudominio.com/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@demo.com", "password": "..."}'
# → {"access": "...", "refresh": "..."}

# Usar el access token (15 min de vida)
curl https://demo.tudominio.com/api/v1/me/ \
  -H "Authorization: Bearer $ACCESS"

# Refrescar (rotación + blacklist del refresh anterior)
curl -X POST https://demo.tudominio.com/api/v1/auth/token/refresh/ \
  -d '{"refresh": "'$REFRESH'"}'

# Logout (blacklistea el refresh)
curl -X POST https://demo.tudominio.com/api/v1/logout/ \
  -H "Authorization: Bearer $ACCESS" -d '{"refresh": "'$REFRESH'"}'
```

**Claims del token**: `user_id`, `email`, `tenant_id`, `tenant_slug`, `role` y
`schema_name`. El claim `schema_name` ata el token al tenant emisor: **un token
de un tenant es rechazado (401) en cualquier otro tenant**.

### 2. API Keys (integraciones servidor-a-servidor)

```bash
# Crear (requiere permiso core.manage_roles)
curl -X POST .../api/v1/api-keys/ -H "Authorization: Bearer $ACCESS" \
  -d '{"name": "integracion-zapier"}'
# → {..., "key": "ak_<prefix>_<secret>"}  ← se muestra UNA sola vez

# Usar
curl .../api/v1/contacts/ -H "X-Api-Key: ak_xxxx_yyyy"
```

Las keys se almacenan hasheadas, pertenecen a un tenant (no funcionan en otro)
y se revocan con `POST /api/v1/api-keys/{id}/revoke/`.

### 3. Sesión + CSRF (páginas servidas por Django)

`GET /api/v1/csrf/` entrega el token; envíalo en `X-CSRFToken` en mutaciones.

## Modelo de autorización

- **Toda ruta de tenant exige membresía activa** en la organización del dominio.
- Operaciones sensibles exigen además un permiso RBAC (`permission_codename`):
  p. ej. `core.manage_roles`, `billing.manage_billing`, `crm.manage_crm`.
- Los roles por defecto (owner/admin/editor/member/viewer) y su mapa de permisos
  viven en `src/core/services/seed.py`.

## Convenciones de respuesta

- **Paginación**: `?page=N` → `{"count", "next", "previous", "results"}` (50/página).
- **Filtros y búsqueda**: `?search=texto` y filtros por campo (`?status=lead`).
- **Errores**: formato DRF `{"detail": "..."}` o `{"campo": ["error", ...]}`.
- **Throttling**: 1000/día autenticado, 100/día anónimo (configurable por env
  `API_USER_RATE`/`API_ANON_RATE`) + límites estrictos de nginx en endpoints de auth.

## Endpoints principales

| Recurso | Ruta | Permiso de escritura |
| --- | --- | --- |
| Perfil propio | `/api/v1/me/` | (propio) |
| Tenant actual | `/api/v1/tenant/` | `core.manage_organization` |
| Miembros + invitaciones | `/api/v1/memberships/` | `core.invite_members`/`core.manage_roles` |
| Roles y permisos | `/api/v1/roles/`, `/api/v1/permissions/` | `core.manage_roles` |
| Planes/Suscripción/Facturas | `/api/v1/plans|subscriptions|invoices/` | `billing.manage_billing` |
| Stripe checkout/portal | `POST /api/v1/subscriptions/checkout|portal/` | `billing.manage_billing` |
| API Keys | `/api/v1/api-keys/` | `core.manage_roles` |
| Audit log | `/api/v1/activity-logs/` | `core.view_audit_logs` |
| Onboarding | `/api/v1/onboarding/...` | (público `start`, rate-limited) |
| CMS · LMS · Community · MCP · CRM | `/api/v1/{cms,lms,community,mcp,crm}/...` | según módulo (flags `ENABLE_*`) |

## Crear endpoints nuevos

Sigue la skill `.claude/skills/scaffold-api-endpoint/` — regla de oro: hereda de
`TenantScopedViewSet` (o usa `PolicyPermission`) y filtra el queryset por
`organization=request_tenant(self.request)`. El test de contraseña de fuego:
`tests/test_api_security.py` debe seguir en verde.
