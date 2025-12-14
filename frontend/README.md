# Frontend (Next.js) — Proyecto Semilla

Este directorio contiene el frontend React/Next.js para `proyecto-semilla` (Django backend).

## Requisitos

- Node.js (LTS) + npm

## Configuración

Crear `.env.local` desde el ejemplo:

```bash
cp .env.local.example .env.local
```

Por defecto:

```bash
DJANGO_BASE_URL=http://localhost:7777
```

## Desarrollo

1) Levantar backend (desde la raíz del repo):

```bash
make dev
```

2) Levantar frontend:

```bash
npm install
npm run dev
```

Abrir `http://localhost:3000`.

Si el puerto `3000` está ocupado, levantar el stack con `FRONTEND_PORT=3001 make dev` y abrir `http://localhost:3001`.

## Notas

- `next.config.ts` define un proxy por `rewrites` para `/api/*` → `${DJANGO_BASE_URL}/api/*`, evitando CORS en dev.
- La guía de migración está en `docs/runbooks/migracion-frontend-nextjs.md`.
