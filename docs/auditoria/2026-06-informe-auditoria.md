# Informe de Auditoría Integral — Proyecto Semilla

**Fecha:** 2026-06-09 · **Alcance:** repositorio completo (backend, frontend, infra, CI/CD, tests, docs)
**Estado de remediación:** los hallazgos marcados ✅ fueron corregidos en la rama de esta auditoría (v0.14.0); los marcados 📋 quedan en el [plan de estabilización](PLAN-ESTABILIZACION.md).

## Resumen ejecutivo

El proyecto tenía una base técnica sólida (multitenancy por schema con RLS, RBAC,
dj-stripe, settings endurecidos en prod, blue-green deploy) pero **no era vendible
como boilerplate** por cuatro problemas estructurales:

1. **Contaminación de producto**: el seed contenía un producto completo (plataforma
   de diagramas Notion/Miro/IA) y 5 marcas mezcladas (Acme, NotionApps, BlockFlow,
   AppNotion, Momentum). ✅ Extirpado.
2. **Fallos críticos de aislamiento multitenant**: cualquier usuario autenticado de
   un tenant podía leer datos (incl. PII de miembros) de otro tenant; un JWT de un
   tenant autenticaba en otro por colisión de IDs entre schemas. ✅ Corregido con
   deny-by-default + binding de JWT, ambos con tests.
3. **Funcionalidad aparente**: páginas que llamaban endpoints inexistentes (billing,
   /me, onboarding), catálogo i18n con 3 de 16 namespaces (la UI mostraba claves
   crudas), datos hardcodeados en dashboard, formularios que simulaban guardar,
   tests de frontend que nunca corrieron (dependencias sin declarar), y un stage
   Docker de producción referenciado pero inexistente. ✅ Corregido.
4. **Afirmaciones no verificables**: README declaraba "100% tests passing (35)" con
   106 tests reales y 22 skips; versiones contradictorias (0.9.1/0.9.2/0.9.3 vs
   CHANGELOG 0.13.0). ✅ Única fuente de versión (pyproject 0.14.0) y claims honestos.

## Hallazgos por severidad

### CRÍTICOS

| # | Hallazgo | Evidencia | Estado |
|---|---|---|---|
| C1 | **Fuga cross-tenant por permisos**: `PolicyPermission` sin codename devolvía `True` sin verificar membresía; `MembershipViewSet` list/retrieve exponía PII de miembros a usuarios de otros tenants; LMS/Community/CMS/MCP/Dashboard solo exigían `IsAuthenticated` | `api/v1/viewsets.py:110-123`, `lms/views.py:31`, `community/views.py:29`, `cms/views.py`, `mcp/views.py` | ✅ `IsTenantMember` + `PolicyPermission` con membresía obligatoria; test `test_cross_tenant_user_cannot_list_other_tenant_members` |
| C2 | **Suplantación vía JWT entre tenants**: usuarios por schema ⇒ IDs colisionan; `JWTAuthentication` resuelve `user_id` en el schema del host ⇒ token del usuario N del tenant A autentica como usuario N del tenant B | `SIMPLE_JWT` + `multitenant/middleware.py` | ✅ claim `schema_name` + `TenantJWTAuthentication`; test `test_jwt_minted_in_one_schema_rejected_in_another` |
| C3 | **Autorización admin solo en cliente con email hardcodeado** (`untalcamilomedina@gmail.com`) y formulario que simulaba guardar | `frontend .../admin/settings/page.tsx:16` | ✅ página eliminada (era además específica del producto) |
| C4 | **Deploy de producción roto**: blue/green referenciaba `target: runner` inexistente en `frontend/Dockerfile` | `compose/docker-compose.blue.yml:38` | ✅ multi-stage con runner standalone non-root |
| C5 | **Identidad del repo**: producto AppNotion + 5 marcas mezcladas | ROADMAP, `src/integrations/`, frontend | ✅ extirpado y rebrandeado |

### ALTOS

| # | Hallazgo | Evidencia | Estado |
|---|---|---|---|
| A1 | Signup sin validadores (solo len≥8), username `email.split("@")[0]` → IntegrityError 500 por colisión, sin rate limit, sin verificación de email | `api/v1/views.py:96-137` | ✅ |
| A2 | Logout `AllowAny` y sin blacklist del refresh token | `api/v1/views.py:88-93` | ✅ |
| A3 | Middleware multitenant: fallback silencioso al schema público ante errores de BD; bypass RLS para superuser era código muerto (corre antes de auth) | `multitenant/middleware.py` | ✅ 503 + código muerto eliminado |
| A4 | Cifrado de campos derivado de `SECRET_KEY` (rotación imposible) con PBKDF2 100k iteraciones POR OPERACIÓN (perf) y fallback silencioso a plaintext | `common/encryption.py` | ✅ `FIELD_ENCRYPTION_KEY` + cache de derivación; 📋 re-cifrado batch para rotación |
| A5 | JWT firmado con `SECRET_KEY` (default inseguro en base) | `settings/base.py:17,288` | ✅ `JWT_SIGNING_KEY` dedicada |
| A6 | `/metrics` Prometheus público | `config/urls.py` | ✅ token Bearer |
| A7 | CORS solo definido en dev; producción sin origins | `settings/dev.py` vs `prod.py` | ✅ env-driven en prod |
| A8 | Webhooks Stripe: `tenant_schema` del payload usado directamente en `schema_context`, sin idempotencia | `billing/webhooks.py` | ✅ `_resolve_tenant` + ledger `StripeEvent` |
| A9 | Frontend llamaba endpoints inexistentes (`/me/`, `/tenant/`, `/logout/`, `/onboarding/start/`, `/api/v1/billing/subscription/`) y no había proxy dev (sin rewrites) | `use-auth.ts`, `billing/page.tsx`, `next.config.ts` | ✅ |
| A10 | `console.log` filtraba contraseña + claves Stripe del onboarding | `lib/api/onboarding.ts:10` | ✅ |
| A11 | Sin lock reproducible: npm requería `--legacy-peer-deps` (Storybook 8 vs Next 16, addon vs vitest 4); Python con rangos abiertos sin lock | `frontend/package.json`, `requirements/` | ✅ npm limpio · 📋 lock Python (pip-tools/uv) |
| A12 | CI: frontend job invocaba scripts inexistentes (`type-check`, `test:run`) — rojo permanente; sin `check --deploy` temprano, sin audit de deps, sin scan de imágenes, sin `permissions:` | `.github/workflows/ci.yml` | ✅ |
| A13 | Subidas CMS sin validación de tipo/tamaño | `cms/views.py:85-96` | ✅ allowlist + límite |
| A14 | Sesiones SOLO en cache Redis con `IGNORE_EXCEPTIONS=True` (Redis caído ⇒ deslogueo masivo silencioso; axes también fail-open) | `settings/base.py` | ✅ `cached_db` · 📋 monitoreo de Redis |
| A15 | Catálogo i18n: 3 de 16 namespaces ⇒ UI con claves crudas en dashboard/billing/members/roles/settings/onboarding | `frontend/messages/*.json` | ✅ 275 claves × 3 idiomas |

### MEDIOS (selección)

| # | Hallazgo | Estado |
|---|---|---|
| M1 | Versionado contradictorio + claims de tests falsos en README + `RESUMEN_PROYECTO.md` inexistente referenciado | ✅ |
| M2 | Datos fake: dashboard (roles "3", usage "12%"), `RecentActivity`/`StatsCards` huérfanos con mocks | ✅ eliminados/conectados a datos reales |
| M3 | API key: scopes decorativos (no se aplican), `mark_used()` escribe en cada request, timing oracle del prefijo | 📋 |
| M4 | `ACCOUNT_EMAIL_VERIFICATION=optional` también en prod | ✅ mandatory en prod (env-overridable) |
| M5 | Settings de test heredan dev (`DEBUG=True`) — los tests no ejercitan configuración de prod | 📋 |
| M6 | CSP con `unsafe-inline` + CDNs (los templates allauth los usan) | 📋 migrar templates → endurecer CSP |
| M7 | deploy.sh: `git pull` sin verificación, path relativo a production.env, sin rollback automático post-switch | 📋 |
| M8 | Celery comparte Redis DB 0 con el cache por defecto | ✅ separable por env (`CELERY_BROKER_URL`) |
| M9 | Settings muertos: `STATICFILES_STORAGE` (eliminado en Django 5.1), `SECURE_BROWSER_XSS_FILTER` (obsoleto) | ✅ |
| M10 | `any` en TypeScript (23 errores eslint), deps muertas (`crypto-js`, `@capacitor/*`, `next-pwa`, `reactflow`, `openapi-fetch`), deps de test sin declarar | ✅ 0 errores eslint; deps depuradas |
| M11 | Gaps de tests: aislamiento cross-tenant, permisos por endpoint, ciclo refresh JWT, idempotencia webhooks, e2e frontend | ✅ parcial (`test_api_security.py`) · 📋 matriz completa + Playwright |
| M12 | JWT toma el "primer" membership activo si el usuario pertenece a varios tenants | 📋 selector de tenant explícito |
| M13 | nginx sin rate limiting ni HSTS; `X-XSS-Protection` obsoleto; body 50M | ✅ |
| M14 | `local.env.example` con variables `AWS_*` que settings nunca lee | ✅ `S3_*` |
| M15 | Componentes de marketing muertos en frontend (About/Pricing/Services/Process/Team/Footer sin importar) | 📋 decidir: landing completa o eliminarlos |

### BAJOS (selección)

`request_tenant` duplicado en 4 módulos (✅ centralizado en `common.api.tenancy`) ·
imports duplicados (✅) · naming `api_key_hash` para un campo cifrado (📋) ·
`client_max_body_size` 50M (✅ 25M) · TODOs inline (✅ los críticos) · Storybook
mínimo (📋 ampliar stories del design system) · docs MkDocs desactualizadas
respecto a la realidad post-Next.js (📋 revisión de `docs/*.md`).

## Verificación realizada en esta rama

- `python3 -m compileall src tests` ✅
- Frontend: `npm ci` limpio (sin legacy-peer-deps) · `npm run lint` 0 errores ·
  `npm run type-check` ✅ · `npm run test` 15/15 ✅ · `npm run build` ✅
- YAML de compose validado; JSON de i18n/claude/mcp validados.
- ⚠️ La suite backend (pytest) requiere Postgres y se ejecuta en CI — los tests
  nuevos de `test_api_security.py` siguen el patrón existente (`HTTP_HOST` +
  `schema_context`) y deben validarse en el primer run de CI de esta rama.

## Métricas del repo (post-saneamiento)

- Backend: ~7.3k LOC (sin migraciones) · 10 apps · ~35 endpoints API
- Frontend: ~12k LOC · 30 rutas · 60+ componentes · 15 tests unit
- Tests backend: 113 funciones (106 previas − 13 de producto + 20 nuevas de seguridad… ver CI)
- Commits: 50 · 1 autor · actividad dic-2025 → mar-2026
