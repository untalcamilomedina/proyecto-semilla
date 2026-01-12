# AGENTS.md

> [!IMPORTANT]
> This file is the **PRIMARY SOURCE OF TRUTH** for any AI agent working on this project. Read it completely before starting any task.

## Table of Contents
1. [Context](#context)
2. [Tech Stack](#tech-stack)
3. [Setup Commands](#setup-commands)
4. [Design System](#design-system)
5. [Architecture & Security Rules](#architecture--security-rules)
6. [Performance Standards](#performance-standards)
7. [Directory Structure](#directory-structure)
8. [Coding Standards (Vibe Coding)](#coding-standards-vibe-coding)

## Context
**Proyecto Semilla** is a SaaS boilerplate built for scalability, security, and offline-first usage.
- **Architecture**: Hybrid (Django REST Backend + Next.js Frontend).
- **Core Principles**:
  - **Stateless**: The backend must remain stateless.
  - **PWA OfflineFirst**: The frontend must work offline using encrypted IndexedDB.
  - **Secure by Default**: No hardcoded secrets. strict CSP/CORS.

## Tech Stack
### Backend
- **Framework**: Django 5.x (DRF)
- **Database**: PostgreSQL (Multi-tenant via `django-tenant-schemas`)
- **Async**: Celery + Redis

### Frontend
- **Framework**: Next.js 15.x (App Router)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4 + Radix UI + Lucide React
- **State**: TanStack Query v5 (Server) + Zustand (Auth/Tenant State)
- **Storage**: IndexedDB (`dexie` + `crypto-js` for AES encryption)
- **i18n**: `next-intl` (Comprehensive coverage)

## Setup Commands
> [!WARNING]
> ALWAYS run commands inside Docker containers. DO NOT run on host.

- **Start API & Frontend**: `make dev` (or `docker compose up -d`)
- **Backend Shell**: `docker exec -it compose-web-1 python manage.py shell`
- **Run Tests**: `docker exec compose-web-1 pytest`
- **Frontend Build**: `cd frontend && npm run build`

## Design System
The system implements **Two Distinct Styles** that coexist:

### 1. Glassmorphism Elite (Unified Styling)
Used for: *ENTIRE Dashboard, Auth, Modals, and Cards.*
- **Primary Color**: Neon Green `#0df20d` (Used for active states and primary actions).
- **Secondary Colors**: Blue `#60a5fa`, Purple `#a855f7` (Used for specific enterprise categories).
- **Background**: `bg-black/20`, `bg-white/5` with `backdrop-blur-2xl`.
- **Borders**: Thin `border-white/5` or `border-white/10` with subtle glows.
- **Vibe**: Dark, premium, high-performance, and futuristic.

### 2. Form & Data Integrity
Used for: *Settings, Audit Logs, and Tables.*
- **Philosophy**: Every interactive element must be consistent with the Elite vibe.
- **i18n**: No hardcoded strings. Every label must come from `next-intl`.

## Architecture & Security Rules
1.  **Environment Variables**: usage of `os.environ` or `django-environ` is MANDATORY. Never hardcode URLs like `localhost:3000`.
2.  **Statelessness**: No state in memory. Use Redis for temporary data.
3.  **Offline**: Critical user data must be syncable. Read from Local DB -> Background Sync to API.
4.  **Security**:
    - All IndexedDB data MUST be encrypted (AES).
    - API keys and secrets in `.env` only.

## Performance Standards
1.  **Observability**: Use `django-silk` to profile slow endpoints.
2.  **Database**: No N+1 queries. Use `select_related` and `prefetch_related`.
3.  **Caching**: Use Redis for expensive computations.

## Directory Structure
- `src/`: Django Backend Source
- `frontend/`: Next.js Frontend Source
  - `src/components/ui/glass/`: Specific Glassmorphism components.
  - `src/lib/storage.ts`: Encrypted Storage Logic.

## Route Inventory (Frontend)
Para facilitar el contexto a los agentes, se mantiene el siguiente mapa de rutas:

- **Auth**: `/login`, `/signup`
- **Dashboard**: `/` (Inicio), `/members`, `/roles`, `/billing`, `/settings`, `/api-keys`, `/audit-logs`
- **Onboarding**: `/onboarding` (Start), `/onboarding/profile`, `/onboarding/organization`, `/onboarding/domain`, `/onboarding/stripe`, `/onboarding/plan`, `/onboarding/payment`, `/onboarding/modules`, `/onboarding/invite`, `/onboarding/review`, `/onboarding/done`

## Coding Standards (Vibe Coding)
1.  **Philosophy**: Code must be "Aesthetic & Robust". It's not just about functioning; it must be readable, well-structured, and delightful.
2.  **Documentation (JSDoc)**:
    - ALL functions, components, and hooks MUST have JSDoc with the `@vibe` tag.
    - Example:
      ```typescript
      /**
       * Renders a glassmorphic card component.
       * 
       * @vibe Elite - Premium container for high-impact content.
       * @param {string} title - The title of the card.
       * @param {ReactNode} children - The content of the card.
       * @returns {JSX.Element} The rendered card.
       */
      ```
3.  **Route Mapping**: Siempre documentar nuevas rutas en el inventario anterior. Esto ahorra tiempo de exploración a las IAs.
4.  **SDK Management**:
    - Se utiliza `drf-spectacular` en el backend para generar el esquema OpenAPI.
    - En el frontend, usa `npm run generate-sdk` para sincronizar los tipos de la API en `src/types/api.ts`.
5.  **SEO Elite**:
    - La Metadata API de Next.js es obligatoria en cada página. Usa `sitemap.ts` y `robots.ts` para control de rastreo.
6.  **GEO (Generative Engine Optimization)**:
    - **Marcado Semántico**: Usa HTML5 (main, section, article, nav) para facilitar el parsing de LLMs.
    - **Structured Data**: Implementa JSON-LD en páginas de alto valor para mejorar la citación por IAs.
    - **Claridad**: Los títulos y descripciones deben ser factuales y directos, optimizados para respuestas de IA.
7.  **Indexación Selectiva**:
    - Solo páginas públicas (`/`, `/login`, `/docs`) deben ser indexadas.
    - Rutas privadas (`/dashboard/*`, `/onboarding/*`) deben tener metadatos `robots: { index: false, follow: false }`.
8.  **MCP Infrastructure**:
    - El módulo `src/mcp` actúa como un **Registry** para servidores MCP externos/internos. Permite a los tenants orquestar herramientas de IA con trazabilidad y seguridad (RBAC).
9.  **Python Docstrings**: Use Google Style docstrings for all Python methods.
10. **No Placeholders**: Build complete features.

