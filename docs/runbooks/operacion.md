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

## GDPR — derechos del interesado

| Solicitud | Comando |
| --- | --- |
| Acceso/portabilidad (art. 15/20) | `python manage.py export_user_data --email X [--output f.json]` |
| Olvido (art. 17) | `python manage.py delete_user_data --email X --yes` |

El borrado **anonimiza** (email/username/nombres irreversibles, cuenta
desactivada, contraseña inutilizable) conservando la fila para integridad de
auditoría y billing. Ejecuta ambos comandos dentro del contenedor web. Plazo
legal de respuesta: 30 días — deja registro de cada solicitud atendida.

## Prueba de carga (línea base)

```bash
make seed && make load-test     # k6: 20 VUs, 1 min, p95<500ms
```

Versiona tus umbrales en `scripts/load/k6-baseline.js` y corre la prueba antes
de cada release mayor. Sin números, "escala" es solo una promesa.

## CI sin costo — alternativas a los minutos de GitHub Actions

Los repos **privados** tienen minutos limitados (plan Free: 2.000/mes). Opciones,
en orden de recomendación:

1. **Hacer el repo público** → Actions pasa a ser **gratis e ilimitado**. Es
   además la ruta open-core del proyecto (playbook cal.com/Supabase). Antes de
   cambiar visibilidad: barrido de secretos (`git log -p | grep -iE "sk_live|AKIA"`,
   y la pestaña Security → Secret scanning).
2. **Optimizar consumo** (ya aplicado en este repo): `paths-ignore` para
   docs/markdown (cero minutos en cambios documentales), matriz de Python
   completa solo en push a `main`, Trivy solo en `main`, Dependabot mensual
   con máximo 3 PRs por ecosistema, `concurrency` con cancelación.
3. **Self-hosted runner**: un VPS de ~5 USD o tu propia máquina ejecuta los
   jobs (minutos ilimitados). `Settings → Actions → Runners → New self-hosted
   runner` y cambia `runs-on: ubuntu-latest` por `runs-on: self-hosted`.
   ⚠️ NUNCA uses self-hosted en un repo público que acepte PRs de forks
   (ejecución de código ajeno en tu máquina).
4. **`make ci-local`**: reproduce los gates del CI en tu máquina sin gastar
   un minuto (lint, mypy, pytest, frontend, build). Para validar antes de
   pushear o mientras no haya cuota. Los agentes de IA lo tienen vía MCP.
5. **`act`** (github.com/nektos/act): ejecuta los workflows reales de
   `.github/workflows/` en Docker local — útil para depurar el propio CI.

## Checklist de repo público (hacer una sola vez tras cambiar visibilidad)

En GitHub → Settings del repo (5 minutos, en este orden):

1. **Code security** → activa **Secret scanning** + **Push protection** +
   **Dependabot alerts** (gratis en repos públicos). Push protection bloquea
   commits con credenciales ANTES de que lleguen al historial.
2. **Branches → Add branch ruleset** para `main`: ✅ Require a pull request
   before merging · ✅ Require status checks to pass — selecciona:
   `lint (3.12)`, `test (3.12)`, `security-audit`, `frontend`, `deploy-smoke`,
   `docker-build` · ✅ Block force pushes. (El check `test (3.13)` solo existe
   en push a main: NO lo marques como requerido en PRs.)
3. **Actions → General**: Workflow permissions = **Read repository contents**
   (los workflows que necesitan más ya lo declaran explícitamente).
4. **General**: añade description y topics (`django`, `nextjs`, `saas`,
   `boilerplate`, `multitenant`, `ai-first`, `mcp`) — es tu SEO en GitHub.
   Activa **Discussions** (los issue templates ya enlazan ahí) y, si quieres
   que cualquiera arranque su SaaS con un clic, marca **Template repository**.
5. **Regla permanente**: JAMÁS registres un self-hosted runner en este repo
   ahora que es público (los PRs de forks ejecutarían código en tu máquina).

Notas de seguridad ya aplicadas en el código para el modo público:
- `claude.yml` solo responde a OWNER/MEMBER/COLLABORATOR (sin esto, cualquier
  persona podría gastar tu API key o intentar prompt injection).
- Ningún workflow usa `pull_request_target` ni self-hosted runners.
- Historial auditado: cero secretos (los env reales nunca se commitearon).
