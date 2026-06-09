# Security Policy

## Versiones soportadas

| Versión | Soporte |
| --- | --- |
| 0.14.x | ✅ |
| < 0.14 | ❌ |

## Reportar una vulnerabilidad

Por favor repórtala de forma **privada**:

1. GitHub → pestaña *Security* → *Report a vulnerability* (Private Vulnerability Reporting), o
2. Contacta al mantenedor del repositorio directamente.

Incluye pasos de reproducción, impacto estimado y propuesta de mitigación si aplica.
No abras issues públicos con detalles explotables. Respuesta objetivo: 72 horas.

## Modelo de seguridad del boilerplate

Garantías que el seed aplica por diseño (ver tests en `tests/test_api_security.py`):

- **Aislamiento multitenant**: todo endpoint de tenant exige membresía activa
  (`common.api.permissions.IsTenantMember` / `PolicyPermission`); los querysets se
  filtran por `request.tenant`; RLS de Postgres como defensa en profundidad.
- **JWT con binding de schema**: un token emitido en un tenant no autentica en otro
  (claim `schema_name`, ver `api.authentication.TenantJWTAuthentication`).
- **Endpoints públicos** (signup/login/onboarding) con rate limiting (django-ratelimit
  + django-axes) y validadores de contraseña de Django.
- **Secretos**: solo por variables de entorno; campos sensibles cifrados en BD con
  `FIELD_ENCRYPTION_KEY` (Fernet); claves dedicadas para JWT y métricas.
- **Webhooks Stripe**: firma verificada por dj-stripe, metadata validada contra BD
  e idempotencia por `event_id`.
- **Producción**: `manage.py check --deploy` en CI, HSTS, cookies Secure,
  SECRET_KEY validado al arranque, contenedores non-root, CSP activa.

## Checklist de hardening al desplegar

- [ ] `DJANGO_SECRET_KEY`, `FIELD_ENCRYPTION_KEY`, `JWT_SIGNING_KEY` únicos y aleatorios
- [ ] `DEBUG=false`, `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`/`CORS_ALLOWED_ORIGINS` explícitos
- [ ] TLS terminado (LB o nginx) con redirección a HTTPS
- [ ] `METRICS_TOKEN` definido si Prometheus scrapea `/metrics`
- [ ] Backups de Postgres y rotación de credenciales programadas
