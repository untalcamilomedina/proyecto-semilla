---
name: infra-hardening
description: Hardening de Docker, Compose, health checks, Gunicorn, .dockerignore y dependency management
author: Mayordomos Dev Team
version: 1.0.0
---

# Skill: Infrastructure Hardening para BlockFlow SaaS

Esta skill guia el hardening de la infraestructura Docker/Compose, configuracion de Gunicorn para produccion, health checks de servicios, .dockerignore, y gestion segura de dependencias.

## Prerrequisitos

- [ ] Dockerfile multi-stage existente
- [ ] docker-compose.yml con servicios web, postgres, redis, minio
- [ ] Makefile con comandos de desarrollo

## Cuando Usar

Usar esta skill cuando:
- Containers corren como root
- Imagenes Docker no estan pineadas a version especifica
- No hay health checks en docker-compose
- Gunicorn corre con 1 worker
- No existe .dockerignore en la raiz del proyecto
- Requirements no tienen lock file

## Proceso

### Paso 1: Non-Root User en Dockerfile

**Archivo:** `/Dockerfile`

```dockerfile
FROM python:3.12.8-slim-bookworm AS runtime

# Crear usuario no-root
RUN groupadd --system app && \
    useradd --system --gid app --create-home app

WORKDIR /app

# Copiar wheels e instalar
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copiar codigo
COPY src/ /app/src/
COPY manage.py /app/

# Cambiar a usuario no-root
USER app

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--chdir", "/app/src", \
     "--workers", "4", \
     "--worker-class", "gthread", \
     "--threads", "2", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

### Paso 2: Pinear Imagenes Base

```dockerfile
# Builder
FROM python:3.12.8-slim-bookworm AS builder

# Runtime
FROM python:3.12.8-slim-bookworm AS runtime

# Frontend
FROM node:20-alpine3.19 AS base
```

### Paso 3: .dockerignore en Raiz

**Archivo:** `/.dockerignore`

```dockerignore
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
.venv
venv
.mypy_cache
.pytest_cache
.ruff_cache
htmlcov
.coverage

# Node
node_modules
frontend/node_modules
frontend/.next

# Environment
.env
.env.*
local.env

# IDE
.vscode
.idea
*.swp
*.swo

# Docker
docker-compose*.yml
compose/
Dockerfile

# Docs & CI
docs/
.github/
.pre-commit-config.yaml
*.md
!README.md

# OS
.DS_Store
Thumbs.db

# Data
celerybeat-schedule
*.sqlite3
media/
```

### Paso 4: Health Checks en docker-compose

**Archivo:** `/compose/docker-compose.yml`

```yaml
services:
  postgres:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

  web:
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s

  minio:
    image: minio/minio:RELEASE.2024-11-07T00-52-20Z
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 10s
      timeout: 5s
      retries: 3
```

### Paso 5: Environment Variables via env_file (No Hardcodear)

**Archivo:** `/compose/docker-compose.yml`

```yaml
services:
  web:
    env_file:
      - ../local.env
    environment:
      # Solo overrides especificos de Docker networking
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/acme_saas
      - REDIS_URL=redis://redis:6379/0
      - S3_ENDPOINT_URL=http://minio:9000
      - EMAIL_HOST=mailpit
```

### Paso 6: Gunicorn para Produccion

**Archivo:** `/deploy/flyio/fly.toml`

```toml
[processes]
  web = "gunicorn config.wsgi:application --bind 0.0.0.0:8000 --chdir /app/src --workers 4 --worker-class gthread --threads 2 --timeout 120 --graceful-timeout 30"
  worker = "celery -A config.celery worker -l info --concurrency 4"
  beat = "celery -A config.celery beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"

kill_timeout = 30  # Aumentar de 5s a 30s
```

### Paso 7: Frontend Production Stage

**Archivo:** `/frontend/Dockerfile`

```dockerfile
FROM node:20-alpine3.19 AS base
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

# Dev stage
FROM base AS dev
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
EXPOSE 3010
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3010"]

# Build stage
FROM base AS build
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM base AS production
RUN addgroup --system app && adduser --system --ingroup app app
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public
USER app
EXPOSE 3010
CMD ["node", "server.js"]
```

### Paso 8: Dependency Lock File

```bash
# Instalar pip-tools
pip install pip-tools

# Generar lock files
pip-compile requirements/base.txt -o requirements/base.lock
pip-compile requirements/prod.txt -o requirements/prod.lock
pip-compile requirements/dev.txt -o requirements/dev.lock
```

**Fix cryptography duplicado en `requirements/base.txt`:**
```
# Remover la linea duplicada:
# cryptography>=0.24.0  <-- ELIMINAR
cryptography>=42.0.0    # <-- MANTENER
```

**Mover django-silk a dev.txt:**
```
# requirements/dev.txt
-r base.txt
django-silk>=5.0.0
django-debug-toolbar>=4.0
```

### Paso 9: Resource Limits en Compose

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'

  worker:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'

  postgres:
    deploy:
      resources:
        limits:
          memory: 1G

  redis:
    deploy:
      resources:
        limits:
          memory: 512M
```

## Checklist de Verificacion

### Obligatorio
- [ ] Dockerfile usa usuario non-root (`USER app`)
- [ ] Imagenes base pineadas a version especifica (no `latest`)
- [ ] `.dockerignore` existe en raiz del proyecto
- [ ] Health checks en postgres, redis, web, minio
- [ ] `depends_on` con `condition: service_healthy`
- [ ] Gunicorn con 4+ workers y timeouts configurados
- [ ] `kill_timeout` >= 30s en fly.toml
- [ ] cryptography duplicado removido de requirements
- [ ] django-silk movido a dev.txt
- [ ] Frontend Dockerfile con production stage

### Recomendado
- [ ] Lock files generados con pip-compile
- [ ] Resource limits en compose
- [ ] Redis con `maxmemory` y eviction policy
- [ ] Named Docker network
- [ ] Celery worker/beat con health checks en fly.toml
- [ ] Backup script para PostgreSQL

## Errores Comunes

### Error: Permission denied al escribir archivos en container
**Causa:** Se cambio a non-root user pero los archivos del COPY son owned by root
**Solucion:** Agregar `--chown=app:app` a los COPY commands

### Error: `pg_isready` no encontrado en healthcheck
**Causa:** Imagen base no incluye pg_isready
**Solucion:** Usar `postgres:16-alpine` que incluye el binario

### Error: Gunicorn worker timeout
**Causa:** Workers insuficientes para la carga
**Solucion:** Formula: `workers = (2 * CPU_CORES) + 1`, agregar `--timeout 120`

## Referencias

- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)
- [Fly.io Django Deploy](https://fly.io/docs/django/)
- [pip-tools Documentation](https://pip-tools.readthedocs.io/)

---

*Ultima actualizacion: 2026-02-05*
