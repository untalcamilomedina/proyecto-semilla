# Roadmap - Proyecto Semilla v0.9.1

> Documento actualizado: 27 de diciembre de 2025
> Versión actual: **v0.9.1**
> Estado: **Estable, en desarrollo activo**

---

## Tabla de Contenidos

1. [Estado Actual del Proyecto](#estado-actual-del-proyecto)
2. [Auditoría de Librerías Django](#auditoría-de-librerías-django)
3. [Plan de Trabajo por Fases](#plan-de-trabajo-por-fases)
4. [Próximas Versiones](#próximas-versiones)
5. [Historial de Cambios](#historial-de-cambios)

---

## Estado Actual del Proyecto

### Resumen Ejecutivo

**Proyecto Semilla** es un boilerplate SaaS enterprise-ready basado en:
- **Backend**: Django 5.2.9 + DRF 3.15 + PostgreSQL (multitenancy schema-based)
- **Frontend**: Next.js 16 + React 19 + Tailwind CSS + Glass UI
- **Infraestructura**: Docker Compose + Celery + Redis + MinIO (S3)

### Stack Tecnológico Actual

| Capa | Tecnología | Versión | Estado |
|------|------------|---------|--------|
| Framework | Django | 5.2.9 | ✅ Estable |
| API | Django REST Framework | 3.15+ | ✅ Operativo |
| OpenAPI | drf-spectacular | 0.28+ | ✅ Documentado |
| Auth | django-allauth | 0.61+ | ✅ Email + Social |
| Permisos | django-guardian + rules | 2.4+/3.3+ | ✅ RBAC granular |
| Feature Flags | django-waffle | 4.0+ | ✅ Configurado |
| Multitenancy | Custom schema-based | - | ✅ Operativo |
| Billing | Stripe (nativo) | 11.0+ | ✅ Webhooks activos |
| Cache | Redis | 5.0+ | ✅ Session + Cache |
| Tasks | Celery | 5.4+ | ✅ Worker + Beat |
| Storage | django-storages + boto3 | 1.14+ | ✅ S3/MinIO |
| Seguridad | django-csp, django-axes, django-ratelimit | varios | ✅ Hardened |
| Observabilidad | Sentry + Prometheus | 2.0+/0.20+ | ✅ Métricas |
| Frontend | Next.js + React | 16/19 | ✅ PWA ready |

### Funcionalidades Implementadas

#### Backend (100% API-first)

| Módulo | Funcionalidad | Estado | Cobertura Tests |
|--------|---------------|--------|-----------------|
| **Core** | Usuarios, Roles, Permisos, Membresías | ✅ Completo | 70% |
| **Multitenant** | Schema-based, Dominios, Branding | ✅ Completo | 60% |
| **Billing** | Planes, Precios, Suscripciones, Webhooks Stripe | ✅ Completo | 55% |
| **API** | REST v1, API Keys, OpenAPI | ✅ Completo | 65% |
| **OAuth** | Login/Signup rate-limited, Allauth | ✅ Completo | 50% |
| **Onboarding** | Wizard 6 pasos, State machine | ✅ Completo | 75% |
| **CMS** | Wagtail (opcional) | ⚠️ Feature flag | 0% |
| **LMS/Community/MCP** | Módulos opcionales | ⚠️ Scaffold only | 0% |

#### Frontend (Next.js)

| Página | Funcionalidad | Estado |
|--------|---------------|--------|
| `/login`, `/signup` | Autenticación estilizada | ✅ Completo |
| `/dashboard` | Panel con métricas del tenant | ✅ Completo |
| `/members` | Tabla + búsqueda + invitación | ✅ Completo |
| `/roles` | CRUD de roles | ✅ Completo |
| `/billing` | Suscripciones + facturas | ✅ Completo |
| `/onboarding/*` | Wizard 6 pasos | ✅ Completo |
| `/settings` | Configuración de cuenta | ⚠️ Pendiente |

### Métricas del Proyecto

```
Versión:           v0.9.1
Líneas de código:  ~15,000 (Python) + ~8,000 (TypeScript)
Apps Django:       10 (6 core + 4 opcionales)
Endpoints API:     33 rutas
Tests:             20 (14 pasando, 6 fallando)
Cobertura:         58.57% (objetivo: 90%)
```

---

## Auditoría de Librerías Django

### Librerías Ya Implementadas ✅

| Librería | Uso Actual | Aprovechamiento |
|----------|------------|-----------------|
| `djangorestframework` | API REST | 100% |
| `drf-spectacular` | OpenAPI docs | 90% |
| `django-allauth` | Auth email + social | 80% |
| `django-guardian` | Permisos por objeto | 70% |
| `rules` | Predicados RBAC | 60% |
| `django-waffle` | Feature flags | 40% |
| `django-filter` | Filtros DRF | 80% |
| `django-csp` | Content Security Policy | 100% |
| `django-axes` | Brute force protection | 100% |
| `django-ratelimit` | Rate limiting | 100% |
| `django-storages` | S3/MinIO | 100% |
| `celery` | Tareas async | 50% |
| `stripe` | Billing nativo | 90% |
| `sentry-sdk` | Error tracking | 80% |
| `prometheus-client` | Métricas | 70% |
| `whitenoise` | Static files | 100% |

### Librerías Recomendadas para Agregar

#### Prioridad Alta (v1.0)

| Librería | Beneficio | Caso de Uso |
|----------|-----------|-------------|
| `dj-stripe` | Sincronización completa con Stripe | Reemplazar integración manual por modelos sync |
| `django-anymail` | ESP integration (Sendgrid, SES) | Emails transaccionales profesionales |
| `django-silk` | Profiling de queries | Optimización de performance |
| `django-lifecycle` | Hooks de modelo | Simplificar signals |
| `pytest-factoryboy` | Integración factory-boy | Tests más limpios |

#### Prioridad Media (v1.1)

| Librería | Beneficio | Caso de Uso |
|----------|-----------|-------------|
| `django-redis` | Redis cache backend | Reemplazar cache básico |
| `django-health-check` | Health checks avanzados | Kubernetes readiness |
| `django-two-factor-auth` | 2FA/MFA | Seguridad enterprise |
| `django-import-export` | Import/export Excel/CSV | Admin avanzado |
| `django-model-utils` | Utilidades de modelos | TimeStampedModel, StatusModel |

#### Prioridad Baja (v1.2+)

| Librería | Beneficio | Caso de Uso |
|----------|-----------|-------------|
| `django-elasticsearch-dsl` | Full-text search | Búsqueda avanzada |
| `django-modeltranslation` | i18n de modelos | Contenido multi-idioma |
| `django-activity-stream` | Activity feeds | Timeline de actividad |
| `django-notifications-hq` | Sistema de notificaciones | Push + email |
| `django-celery-results` | Almacenar resultados | Debugging de tareas |

### Librerías NO Recomendadas

| Librería | Razón |
|----------|-------|
| `django-tenants` | Ya tienes multitenancy custom funcionando |
| `django-rest-auth` | Obsoleta, ya usas allauth |
| `drf-yasg` | Ya usas drf-spectacular (mejor) |
| `django-debug-toolbar` | Solo dev, ya tienes silk/sentry |

---

## Plan de Trabajo por Fases

### Fase 1: Estabilización y Calidad (v1.0) - Enero 2025

**Objetivo**: Llevar cobertura de tests a 90% y corregir regresiones.

#### 1.1 Corrección de Tests Fallantes
- [ ] Analizar los 6 tests fallando
- [ ] Corregir fixtures de multitenancy
- [ ] Actualizar mocks de Stripe
- [ ] Validar API endpoints con schema

#### 1.2 Aumento de Cobertura
- [ ] Tests unitarios para `billing/webhooks.py`
- [ ] Tests de integración para `multitenant/middleware.py`
- [ ] Tests E2E del flujo onboarding completo
- [ ] Tests de API keys y autenticación

#### 1.3 Migración a dj-stripe
- [ ] Instalar `dj-stripe>=2.10`
- [ ] Migrar modelos: Plan → djstripe.Product, Price → djstripe.Price
- [ ] Configurar webhooks automáticos
- [ ] Deprecar `billing/webhooks.py` manual

#### 1.4 Email Transaccional
- [x] Instalar `django-anymail>=10.0`
- [x] Configurar backend (Sendgrid, SES o Mailgun)
- [x] Templates de email: Welcome, Invite, Password Reset
- [x] Integrar con onboarding

### Fase 2: Performance y Observabilidad (v1.1) - Febrero 2025

**Objetivo**: Optimizar queries y mejorar monitoreo.

#### 2.1 Profiling
- [x] Instalar `django-silk>=5.0`
- [x] Configurar middleware de profiling
- [x] Identificar queries N+1
- [x] Optimizar viewsets con `select_related`/`prefetch_related`

#### 2.2 Caching Avanzado
- [x] Instalar `django-redis>=5.4`
- [x] Configurar cache de sesiones
- [x] Cache de queries frecuentes (Dashboard)
- [x] Invalidación automática (TTL)

#### 2.3 Health Checks
- [ ] Instalar `django-health-check>=3.18`
- [ ] Agregar checks: DB, Redis, Celery, Storage
- [ ] Integrar con `/readyz` existente
- [ ] Configurar alertas

### Fase 3: Seguridad Enterprise (v1.2) - Marzo 2025

**Objetivo**: Implementar 2FA y auditoría avanzada.

#### 3.1 Autenticación de Dos Factores
- [ ] Instalar `django-two-factor-auth>=1.16`
- [ ] Configurar TOTP (Google Authenticator)
- [ ] Backup codes
- [ ] UI en frontend

#### 3.2 Auditoría Avanzada
- [ ] Instalar `django-auditlog>=3.0`
- [ ] Logging de cambios en modelos críticos
- [ ] Dashboard de auditoría
- [ ] Exportación de logs

#### 3.3 Compliance
- [ ] Revisión OWASP Top 10
- [ ] Headers de seguridad adicionales
- [ ] Rotación automática de API keys
- [ ] Política de contraseñas configurable

### Fase 4: Funcionalidades Enterprise (v1.3) - Abril 2025

**Objetivo**: Features para clientes enterprise.

#### 4.1 Import/Export
- [ ] Instalar `django-import-export>=4.0`
- [ ] Exportar: Miembros, Roles, Facturas
- [ ] Importar: Usuarios bulk
- [ ] Formatos: Excel, CSV, JSON

#### 4.2 Notificaciones
- [ ] Instalar `django-notifications-hq>=1.8`
- [ ] Notificaciones in-app
- [ ] Preferencias de usuario
- [ ] Integración con email

#### 4.3 Búsqueda Avanzada
- [ ] Evaluar `django-watson` vs `elasticsearch`
- [ ] Búsqueda full-text en miembros/roles
- [ ] Autocompletado
- [ ] Filtros avanzados

### Fase 5: Módulos Opcionales (v2.0) - Q2 2025

**Objetivo**: Activar y completar módulos feature-flagged.

#### 5.1 CMS (Wagtail)
- [ ] Activar `ENABLE_CMS=True`
- [ ] Configurar páginas base
- [ ] Blog corporativo
- [ ] Landing pages

#### 5.2 LMS
- [ ] Modelo: Course, Lesson, Enrollment
- [ ] API completa
- [ ] Player de video
- [ ] Progreso de usuario

#### 5.3 Community
- [ ] Modelo: Post, Comment, Reaction
- [ ] Feed de actividad
- [ ] Moderación
- [ ] Gamificación

---

## Próximas Versiones

### v1.0.0 (Enero 2025)
- [ ] Cobertura de tests >= 90%
- [ ] Migración a dj-stripe
- [ ] Email con django-anymail
- [ ] Documentación completa
- [ ] Deploy de producción validado

### v1.1.0 (Febrero 2025)
- [ ] Profiling con django-silk
- [ ] Cache con django-redis
- [ ] Health checks avanzados
- [ ] Dashboard de métricas

### v1.2.0 (Marzo 2025)
- [ ] 2FA con TOTP
- [ ] Auditoría con django-auditlog
- [ ] Revisión de seguridad
- [ ] Penetration testing

### v1.3.0 (Abril 2025)
- [ ] Import/Export Excel
- [ ] Notificaciones in-app
- [ ] Búsqueda full-text
- [ ] API v2 (breaking changes)

### v2.0.0 (Q2 2025)
- [ ] Módulo CMS activo
- [ ] Módulo LMS activo
- [ ] Módulo Community activo
- [ ] Multi-idioma completo

---

## Historial de Cambios

### v0.9.1 (27/12/2025) - Release Actual
**Agregado:**
- AGENTS.md con estándares para agentes AI
- PWA OfflineFirst con Dexie + crypto-js
- Sistema de diseño Glass UI (GlassCard, GlassButton, GlassModal)
- Configuración Docker flexible con puertos configurables

**Cambiado:**
- Migración HTMX → React + Next.js completada
- CORS/CSRF con variables de entorno
- Puertos Docker en rango 9xxx

**Estado:**
- 14 tests pasando, 6 fallando
- Cobertura: 58.57%
- Sistema funcional y estable

### v0.9.0 (13/12/2025)
**Agregado:**
- Comando `seed_demo` para inicialización
- Páginas de auth estilizadas
- Health checks `/healthz`, `/readyz`, `/metrics`

**Corregido:**
- Múltiples fixes de configuración Docker
- Middleware de Allauth
- CSP migrado a v4.x

### Versiones Anteriores
Ver [CHANGELOG.md](./CHANGELOG.md) para historial completo.

---

## Comandos Útiles

```bash
# Desarrollo
make dev                    # Levantar stack completo
make test                   # Ejecutar tests
make lint                   # Linting con ruff/black
make migrate                # Migraciones Django

# Docker
docker compose -f compose/docker-compose.yml --env-file env/.env up -d
docker compose -f compose/docker-compose.yml --env-file env/.env exec web python manage.py migrate
docker compose -f compose/docker-compose.yml --env-file env/.env exec web python manage.py seed_demo

# Tests
pytest --cov=src --cov-report=html
pytest -x -k "test_billing"
pytest --tb=short

# Producción
python manage.py check --deploy
python manage.py collectstatic --no-input
```

---

## Contribución

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit con mensaje descriptivo
4. Push y crear Pull Request
5. Esperar revisión de código

---

## Contacto

- **Issues**: [GitHub Issues](https://github.com/untalcamilomedina/proyecto-semilla/issues)
- **Documentación**: [docs/](./docs/)
- **Changelog**: [CHANGELOG.md](./CHANGELOG.md)
