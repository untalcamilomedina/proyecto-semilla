# Runbook — Desarrollo local

## Arranque

```bash
make dev
```

Servicios incluidos:

- web (Django) en `http://localhost:7777`
- frontend (Next.js) en `http://localhost:3000`
- worker / beat (Celery)
- postgres / redis
- minio (S3 dev)
- mailpit (SMTP dev)

Si el puerto `3000` está ocupado, usar: `FRONTEND_PORT=3001 make dev`

## Migraciones

```bash
docker compose -f compose/docker-compose.yml exec web python manage.py migrate
docker compose -f compose/docker-compose.yml exec web python manage.py migrate_tenants
```

## Seed demo

```bash
docker compose -f compose/docker-compose.yml exec web python manage.py create_tenant "Acme" acme
docker compose -f compose/docker-compose.yml exec web python manage.py seed_rbac
docker compose -f compose/docker-compose.yml exec web python manage.py seed_billing
```

Para crear el tenant demo recomendado (incluye dominios `localhost`/`127.0.0.1`):

```bash
make seed
```

## Frontend (Next.js)

- Guía: `docs/runbooks/migracion-frontend-nextjs.md`
- Variables: copiar `frontend/.env.local.example` → `frontend/.env.local`
