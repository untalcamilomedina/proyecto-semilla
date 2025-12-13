# Runbook — Desarrollo local

## Arranque

```bash
make dev
```

Servicios incluidos:

- web (Django)
- worker / beat (Celery)
- postgres / redis
- minio (S3 dev)
- mailpit (SMTP dev)

## Migraciones

```bash
python manage.py migrate_tenants
```

## Seed demo

```bash
python manage.py create_tenant "Acme" acme
python manage.py seed_rbac
python manage.py seed_billing
```

