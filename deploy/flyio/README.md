# Fly.io deploy (E2E)

Esta receta despliega el boilerplate en Fly.io usando el `Dockerfile` multi‑stage y multitenancy por schema.

## Prerrequisitos

- `flyctl` instalado y autenticado.
- Un dominio base configurado para subdominios (`*.acme.dev` o tu equivalente).

## Pasos

1. **Crear app**

   ```bash
   flyctl launch --no-deploy
   ```

   Copia/edita `deploy/flyio/fly.toml` y ajusta:
   - `app`
   - `primary_region`
   - `DOMAIN_BASE` (como secreto/env)

2. **Postgres**

   ```bash
   flyctl postgres create
   flyctl postgres attach --app <app> <postgres-app>
   ```

3. **Redis**

   Usa Upstash o Fly Redis:

   ```bash
   flyctl redis create
   flyctl redis attach --app <app> <redis-app>
   ```

4. **Secrets**

   ```bash
   flyctl secrets set \
     DJANGO_SECRET_KEY=... \
     DATABASE_URL=... \
     REDIS_URL=... \
     STRIPE_SECRET_KEY=... \
     STRIPE_WEBHOOK_SECRET=... \
     S3_ENDPOINT_URL=... \
     S3_BUCKET_NAME=... \
     S3_ACCESS_KEY=... \
     S3_SECRET_KEY=... \
     SENTRY_DSN=... \
     ALLOWED_HOSTS=acme.dev,*.acme.dev \
     CSRF_TRUSTED_ORIGINS=https://acme.dev,https://*.acme.dev \
     DOMAIN_BASE=acme.dev
   ```

5. **Deploy**

   ```bash
   make deploy
   ```

   El deploy ejecuta:
   - `migrate_tenants` como `release_command`
   - `collectstatic`

6. **Workers**

   Para Celery:

   ```bash
   flyctl scale count 1 --process worker
   flyctl scale count 1 --process beat
   ```

## Health checks

Fly valida:

- `/healthz`
- `/readyz`

## Rollback

```bash
flyctl releases list
flyctl releases revert <version>
```

