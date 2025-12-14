# ADR 0013 — Migración de Frontend a React + Next.js

**Estado:** aceptado (v0.9.1)  
**Decisión:** Introducir un frontend React/Next.js en `frontend/` y migrar gradualmente las vistas HTML actuales (HTMX/Tailwind/Alpine) consumiendo la API DRF.

## Contexto

- En V1 se eligió HTMX + Tailwind + Alpine por CDN (ver ADR 0011) para DX rápida y cero pipeline JS/CSS obligatoria.
- El proyecto ya expone una API DRF versionada (`/api/v1`) y requiere un camino claro para:
  - UI más compleja,
  - reutilización de componentes,
  - SSR/SSG (SEO/performance),
  - PWA y empaquetado nativo.

## Decisión

- Crear una app Next.js dentro del repo en `frontend/`.
- Mantener Django como backend (monolito modular) y **source-of-truth** de negocio.
- Consumir DRF desde React (fetch/axios) y migrar pantalla por pantalla.
- En dev, preferir **proxy por `rewrites`** desde Next.js hacia Django para evitar CORS.
- Mantener auth por sesión cuando aplique; para mutaciones, usar CSRF explícito (endpoint `/api/v1/csrf/`).

## Consecuencias

- Se introduce toolchain Node.js (dependencias, builds, CI).
- Aumenta complejidad operativa (dos apps), pero habilita SSR/SSG, PWA y un roadmap frontend más escalable.

