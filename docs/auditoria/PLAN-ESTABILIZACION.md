# Plan de Estabilización — Proyecto Semilla

> Hoja de ruta para llevar el seed de "estabilizado" (v0.14) a "producto vendible" (v1.0).
> La Fase 0 y la Fase 1 se ejecutaron en la rama de la auditoría — se listan como
> registro y criterio de aceptación. Cada fase tiene entregables verificables.

## ✅ Fase 0 — Identidad (ejecutada en v0.14)

| Entregable | Criterio de aceptación |
|---|---|
| Extirpar producto AppNotion (backend + frontend + tests + docs) | `grep -ri "notion\|miro\|gemini\|diagram"` sin matches de producto |
| Marca única configurable | `PROJECT_NAME` (backend) + `frontend/src/lib/branding.ts`; grep sin Acme/BlockFlow/Momentum/NotionApps |
| Versión única | pyproject = badge README = CHANGELOG (0.14.0) |

## ✅ Fase 1 — Seguridad crítica (ejecutada en v0.14)

| Entregable | Criterio de aceptación |
|---|---|
| Deny-by-default multitenant (`IsTenantMember`, `PolicyPermission` con membresía) | `tests/test_api_security.py::test_cross_tenant_*` en verde |
| Binding JWT por schema | `test_jwt_minted_in_one_schema_rejected_in_another` en verde |
| Endpoints auth endurecidos (logout/blacklist, signup validado + ratelimit) | tests de signup/logout en verde |
| Claves dedicadas (`FIELD_ENCRYPTION_KEY`, `JWT_SIGNING_KEY`), `/metrics` con token | `production.env.example` documenta las 3 claves |
| Webhooks validados + idempotentes; middleware 503; uploads CMS validados | revisión de código + tests existentes de webhooks |

## 📋 Fase 2 — Confianza verificable (1–2 semanas) → v0.15

**Objetivo:** que cada afirmación del README sea demostrable en CI.

1. **Primer run de CI en verde** sobre esta rama: ajustar los tests nuevos si el
   entorno CI revela diferencias (p. ej. dominios `.testserver`, seeds de roles).
2. **Lock de dependencias Python**: adoptar `uv` (o pip-tools): `uv pip compile
   requirements/base.txt -o requirements/base.lock` por entorno; CI instala del lock;
   Renovate/Dependabot programado semanal.
3. **Matriz de aislamiento**: test paramétrico que recorre TODOS los registros del
   router v1 × {anónimo, miembro, no-miembro, viewer, owner} y asegura el código
   de estado esperado. Extender a módulos opcionales (LMS/Community/CMS/MCP).
4. **Cobertura medida y gate realista**: bajar `fail_under` a 70 (medido), subir
   gradualmente; publicar badge desde CI.
5. **E2E Playwright** (3 flujos): login→dashboard, onboarding completo, upgrade
   de plan (con Stripe test mode). Job opcional en CI nightly.
6. **Ciclo JWT completo testeado**: obtain→refresh→rotación→blacklist→reuso rechazado.

## 📋 Fase 3 — Hardening fino (1–2 semanas) → v0.16

1. **CSP estricta**: migrar templates Django (allauth/base) de CDNs a assets
   compilados (Tailwind build local); quitar `unsafe-inline` con nonces; alinear
   CSP de nginx y Django.
2. **Cookies httpOnly para JWT** + middleware SSR en Next para proteger rutas del
   dashboard server-side (hoy la protección es client-side + 401 del API).
3. **API Keys**: aplicar `scopes` en `ApiKeyAuthentication`/permisos; throttle de
   `mark_used()` (update diferido); naming `api_key_hash`→`api_key_encrypted` en MCP.
4. **Selector de tenant en token**: endpoint `auth/token` acepta `tenant` explícito
   cuando el usuario tiene múltiples membresías (hoy toma la primera).
5. **Rotación de claves**: comando `manage.py reencrypt_fields --old-key X` para
   rotar `FIELD_ENCRYPTION_KEY` sin pérdida.
6. **deploy.sh**: rollback automático si el smoke post-switch falla; path absoluto
   de production.env; verificación de firma/ref del git pull.
7. **Settings de test** independientes de dev (`DEBUG=False`, config prod-like).

## 📋 Fase 4 — Experiencia de adopción (2 semanas) → v0.17

1. **`scripts/bootstrap.py`**: instalación interactiva — renombra proyecto/slug,
   genera las 3 claves, escribe local.env, opcionalmente configura branding del
   frontend. Meta: de `git clone` a app corriendo en <10 minutos garantizados.
2. **Docs de extensión**: guía "añade tu módulo" end-to-end (app Django + viewset
   con IsTenantMember + página Next + i18n + tests) referenciando la skill
   `scaffold-full-stack-feature`.
3. **Decidir landing**: completar los componentes de marketing muertos
   (About/Pricing/Services/Team) como landing configurable, o eliminarlos.
4. **Storybook como catálogo vivo**: stories para todos los componentes Glass;
   publicar en Chromatic o estático en CI.
5. **Refrescar `docs/*.md`** (arquitectura, multitenancy, billing, rbac) para
   reflejar el stack actual (Next.js, JWT, dj-stripe) + ADR nuevo: "0014 —
   aislamiento multitenant deny-by-default y binding JWT".
6. **Demo pública** desplegada (Fly.io) con datos de muestra + capturas en README.

## 📋 Fase 5 — Producto vendible (continuo) → v1.0

1. Releases firmados + CHANGELOG generado de commits convencionales (release-please).
2. Plantilla GitHub "Use this template" + guía de actualización del seed para
   proyectos derivados (`git remote add seed` + cherry-pick guiado).
3. Auditoría de seguridad externa + `SECURITY.md` con PGP/contacto formal.
4. SLO de mantenimiento: actualizar Django/Next en <30 días tras release mayor.

## Riesgos y deuda aceptada (documentada)

- **CSP permisiva** hasta Fase 3.1 (los templates allauth dependen de CDNs).
- **Protección de rutas SSR** pendiente hasta Fase 3.2 (tokens en memoria).
- Cobertura backend: 70.16% medida en CI; gate ajustado a 70. Subida gradual en Fase 2.4.
- **Tipos OpenAPI del frontend** (`types/api.ts`) quedaron desactualizados tras
  retirar endpoints de producto: regenerar con `npm run generate-sdk` con el
  backend corriendo (Fase 2.1).
- El claim `schema_name` solo protege tokens NUEVOS; los emitidos antes de v0.14
  no traen claim (aceptable: no hay despliegues productivos conocidos del seed).
