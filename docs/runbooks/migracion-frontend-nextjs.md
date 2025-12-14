# Runbook — Migración Frontend HTMX → React + Next.js (v0.9.1)

Este runbook describe cómo introducir un frontend React/Next.js en `proyecto-semilla` para reemplazar gradualmente las vistas HTML actuales (HTMX/Tailwind/Alpine) consumiendo la API DRF.

> En `v0.9.1` el scaffold `frontend/` ya viene incluido y también está integrado en `compose/docker-compose.yml` como servicio `frontend`.

## 1) Preparar el entorno

- Instalar Node.js (LTS) y npm (o yarn/pnpm).
- Mantener el backend Django corriendo (dev) con Docker Compose:

```bash
make dev
```

Esto levanta:
- Django: `http://localhost:7777`
- Next.js: `http://localhost:3000`
  - Si el puerto `3000` está ocupado: `FRONTEND_PORT=3001 make dev` (Next queda en `http://localhost:3001`)

## 2) Crear el proyecto Next.js

Desde la raíz del repo:

```bash
npx create-next-app@latest frontend
```

Luego:

```bash
cd frontend
```

## 3) Dependencias y tooling

Si durante `create-next-app` no activaste Tailwind, instálalo:

```bash
npm install tailwindcss postcss autoprefixer
```

Y sigue la guía oficial para Next.js: https://tailwindcss.com/docs/guides/nextjs

## 4) Integración Next.js ↔ Django (sin CORS)

La forma más simple para desarrollo es **proxiando** el backend desde Next.js con `rewrites`, para que el navegador consuma `/api/...` en el mismo origen del frontend.

En `v0.9.1` esto ya viene configurado en `frontend/next.config.ts` y en Docker se inyecta `DJANGO_BASE_URL=http://web:8000`.

Ejemplo recomendado en `frontend/next.config.ts`:

```js
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    const backend = process.env.DJANGO_BASE_URL || "http://localhost:7777";
    return [
      { source: "/api", destination: `${backend}/api` },
      { source: "/api/:path*", destination: `${backend}/api/:path*` },
    ];
  },
};

export default nextConfig;
```

Crear `frontend/.env.local` (desde el ejemplo):

```bash
cp frontend/.env.local.example frontend/.env.local
```

### CSRF (para POST/PUT/DELETE con SessionAuth)

En `v0.9.1` existe `GET /api/v1/csrf/` que devuelve `{ "csrfToken": "..." }` y asegura la cookie CSRF.

- Paso 1: hacer `GET /api/v1/csrf/` al iniciar el frontend (o antes de la primera mutación).
- Paso 2: incluir header `X-CSRFToken: <token>` en requests mutantes.

> Compat: también funciona `GET /api/v1/csrf` (sin slash final) para evitar redirects/loops cuando Next actúa como proxy.

## 5) Backend: endpoints útiles para migración

La API ya expone endpoints versionados en `GET /api/v1/...` (DRF).

En `v0.9.1` se agregaron/ajustaron para soportar frontend React:

- `GET /api/v1/tenant/`: incluye `branding` y `domain_base` para theming por tenant.
- `POST /api/v1/memberships/invite/`: invita miembros por lista de emails (equivalente a la vista HTML).

## 6) Migrar vistas HTMX → páginas React

Mapa sugerido (mínimo viable):

- `src/templates/core/dashboard.html` → `frontend` ruta `/` o `/dashboard`
  - Consumir: `GET /api/v1/tenant/`, `GET /api/v1/subscriptions/` (opcional), `GET /api/v1/plans/`
- `src/templates/core/member_list.html` → ruta `/members`
  - Consumir: `GET /api/v1/memberships/`
  - Mutación: `POST /api/v1/memberships/invite/`
- `src/templates/core/role_list.html` → ruta `/roles`
  - Consumir: `GET /api/v1/roles/`
- `src/templates/core/role_form.html` → ruta `/roles/new` y `/roles/[id]/edit`
  - Consumir: `POST /api/v1/roles/`, `PUT/PATCH /api/v1/roles/:id/`
- `src/templates/billing/dashboard.html` → ruta `/billing`
  - Consumir: `GET /api/v1/plans/`, `GET /api/v1/subscriptions/`, `GET /api/v1/invoices/`

Recomendación: migrar **una pantalla por vez** y mantener el resto en Django hasta completar parity.

## 7) Rutas y navegación

- Si usas `pages/`: cada archivo en `frontend/pages/` es una ruta.
- Si usas `app/` (App Router): cada carpeta en `frontend/app/` define rutas y layouts.

## 8) SEO y performance

- Usar SSR/SSG donde aplique (catálogo de planes, landing pública).
- Para páginas privadas (dashboard), SSR puede simplificar auth/cookies.
- Usar `next/image` para optimización de imágenes.

## 9) PWA y empaquetado nativo (opcional)

- Añadir PWA con `next-pwa` (service worker + manifest).
- Empaquetar con Capacitor cuando la PWA esté estable.

## 10) Troubleshooting (dev)

- Si ves `DisallowedHost: 'web:8000'` al consumir `/api/...` desde Next.js:
  - Asegura `USE_X_FORWARDED_HOST=1` en `env/.env.dev.example`
  - Asegura `ALLOWED_HOSTS` incluye `web`/`frontend`/`localhost`
  - Reinicia: `docker compose -f compose/docker-compose.yml restart web frontend`
