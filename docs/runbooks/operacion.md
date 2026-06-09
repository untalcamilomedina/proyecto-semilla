# Operación — Stateless, escalado y mantenimiento

Guía para operar un despliegue del seed de forma profesional. Con esto (y el
arnés de IA del repo) cualquier equipo puede mantener su sistema.

## Arquitectura stateless (12-factor)

Los contenedores de la app **no guardan estado**: puedes matarlos, escalarlos
horizontalmente o reemplazarlos (blue-green) sin pérdida.

| Estado | Dónde vive | Nota |
| --- | --- | --- |
| Datos | **Postgres** (schema por tenant + RLS) | Única fuente de verdad |
| Sesiones | **Postgres** con cache en Redis (`cached_db`) | Un Redis caído NO desloguea |
| JWT | **Sin estado en servidor** (firma `JWT_SIGNING_KEY`) | Blacklist de refresh en Postgres |
| Cache / rate limiting | **Redis** (fail-soft: `IGNORE_EXCEPTIONS`) | Pérdida tolerable |
| Media (uploads) | **S3/MinIO** (`django-storages`) | Configura `S3_*` en prod — nunca disco local |
| Estáticos | Horneados en la imagen (WhiteNoise/standalone) | Idénticos en cada réplica |
| Logs | **stdout JSON** | Agrega con tu plataforma (Loki/CloudWatch/...) |
| Tareas | **Celery** sobre Redis | Workers escalan horizontalmente |

Reglas para mantenerlo stateless:

1. Nunca escribas a disco local en código de negocio — usa `default_storage`.
2. `celery beat` debe correr en **una sola réplica** (los workers, las que quieras).
3. Las migraciones corren ANTES del switch de tráfico (el deploy blue-green ya lo hace).

## Escalado

```bash
# Más réplicas del API y workers (compose prod)
docker compose -f compose/docker-compose.blue.yml up -d --scale web-blue=3 --scale worker-blue=2
```

- **Web**: stateless → escala libre detrás de nginx (`upstream` balancea).
- **Postgres**: vertical primero; réplicas de lectura cuando toque (conexiones
  con `conn_max_age=600` ya activado).
- **Redis**: `maxmemory` configurado; para HA usa un Redis gestionado.
- Límites de recursos por servicio ya definidos en los compose blue/green.

## Checklist de despliegue

1. `production.env` desde `production.env.example` — completa TODAS las claves
   `CHANGE-ME` (`DJANGO_SECRET_KEY`, `FIELD_ENCRYPTION_KEY`, `JWT_SIGNING_KEY`,
   `METRICS_TOKEN`, credenciales de BD/Redis/S3).
2. `bash compose/deploy.sh blue` (primera vez) — build, migraciones, health
   checks y switch de nginx. Siguientes deploys alternan `green`/`blue`.
3. Verifica: `curl https://tudominio.com/readyz` → `{"status":"ready"}`.
4. Prometheus: scrape de `/metrics` con `Authorization: Bearer $METRICS_TOKEN`.

## Mantenimiento periódico

| Frecuencia | Tarea | Cómo |
| --- | --- | --- |
| Diario | Backups de Postgres | `pg_dump` por schema o snapshot gestionado; **prueba el restore** |
| Semanal | Dependencias | CI corre pip-audit/npm audit/Trivy en cada PR; revisa alertas |
| Mensual | Rotación de credenciales de servicio | BD/Redis/S3 (la app las lee por env: rolling restart) |
| Por release | `CHANGELOG.md` + tag + deploy blue-green | El color anterior queda como rollback inmediato |

**Rotación de claves de aplicación**:
- `DJANGO_SECRET_KEY`: rotable — invalida sesiones/CSRF activos, no datos
  (el cifrado de campos usa `FIELD_ENCRYPTION_KEY` y los JWT `JWT_SIGNING_KEY`).
- `JWT_SIGNING_KEY`: rotable — invalida tokens vigentes (los usuarios re-loguean).
- `FIELD_ENCRYPTION_KEY`: **NO rotar sin re-cifrar** (comando de re-cifrado en
  el roadmap, Fase 3.5).

## Operar con el arnés de IA

El repo está preparado para que un agente haga el mantenimiento contigo:

- **Local**: abre el repo con Claude Code — el hook de sesión le da contexto,
  `CLAUDE.md` las reglas y `.claude/skills/` los procedimientos (p. ej.
  `infra-hardening`, `debug-protocol`, `security-hardening`).
- **GitHub**: comenta `@claude investiga este error de producción: <stacktrace>`
  en un issue (workflow `claude.yml` + secret `ANTHROPIC_API_KEY`).
- **Reglas de seguridad para el agente**: ya codificadas en `CLAUDE.md`
  (membresía por tenant, secretos por env, CI debe pasar). Los tests de
  `tests/test_api_security.py` actúan como barandilla: si el agente rompe el
  aislamiento multitenant, el CI lo bloquea.

## Incidentes comunes

| Síntoma | Diagnóstico | Acción |
| --- | --- | --- |
| 503 en todas las rutas | BD caída (el middleware lo reporta así a propósito) | Revisa Postgres; `/healthz` sigue vivo para los probes |
| `readyz` → `degraded` | `checks` indica si es database o cache | Restaura el servicio señalado |
| Usuarios deslogueados masivamente | ¿Rotaste `DJANGO_SECRET_KEY` o `JWT_SIGNING_KEY`? | Esperado: re-login |
| 429 en login | Rate limiting (nginx `auth_zone` + axes) | Verifica origen; ajusta zonas si es legítimo |
| Webhooks Stripe sin efecto | Evento duplicado (idempotencia) o metadata inválida | Logs del worker: `Stripe event ... already processed` / `metadata inconsistente` |
