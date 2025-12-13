# Runbook — Fly.io

Usa la receta en `deploy/flyio/`.

## Deploy

```bash
make deploy
```

## Secrets

Ver `deploy/flyio/README.md`.

## Workers

```bash
flyctl scale count 1 --process worker
flyctl scale count 1 --process beat
```

