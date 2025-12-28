# AGENTS.md

> [!IMPORTANT]
> This file is the **PRIMARY SOURCE OF TRUTH** for any AI agent working on this project. Read it completely before starting any task.

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
- **Framework**: Next.js 16.1.1 (App Router)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4 + Radix UI + Lucide React
- **State**: TanStack Query v5 (Server) + Context (Client)
- **Storage**: IndexedDB (`dexie` + `crypto-js` for AES encryption)
- **i18n**: `next-intl`

## Setup Commands
> [!WARNING]
> ALWAYS run commands inside Docker containers. DO NOT run on host.

- **Start API & Frontend**: `make dev` (or `docker compose up -d`)
- **Backend Shell**: `docker exec -it compose-web-1 python manage.py shell`
- **Run Tests**: `docker exec compose-web-1 pytest`
- **Frontend Build**: `cd frontend && npm run build`

## Design System
The system implements **Two Distinct Styles** that coexist:

### 1. Glass/Dark (Premium/Feature)
Used for: *Cards, Modals, High-impact UI.*
- **Primary**: Neon Green `#0df20d` (`emerald-500`)
- **Background**: `bg-black/40`, `bg-white/5` (Backdrop Blur XL)
- **Borders**: `border-white/10`
- **Shadows**: `.shadow-neon` (Glow effect)

### 2. Clean/Minimal (Structure/Dashboard)
Used for: *Layouts, Forms, Data Tables.*
- **Palette**: Zinc 900 (Text), Zinc 100/White (Bg)
- **Style**: Solid backgrounds, thin borders (`zinc-200`), no blur.

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

## Coding Standards (Vibe Coding)
1.  **Philosophy**: Code must be "Aesthetic & Robust". It's not just about functioning; it must be readable, well-structured, and delightful.
2.  **Documentation (JSDoc)**:
    - ALL JavaScript/TypeScript functions, components, and hooks MUST have JSDoc.
    - Example:
      ```typescript
      /**
       * Renders a glassmorphic card component.
       * @param {string} title - The title of the card.
       * @param {ReactNode} children - The content of the card.
       * @returns {JSX.Element} The rendered card.
       */
      ```
3.  **Python Docstrings**: Use Google Style docstrings for all Python methods.
4.  **No Placeholders**: Never leave `// TODO: Implement later` without a valid reason or fallback. Build complete features.

