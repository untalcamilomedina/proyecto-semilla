# AGENTS.md

## Project Context
**Proyecto Semilla** is a SaaS boilerplate using a hybrid architecture:
- **Backend**: Django REST Framework (Python 3.12+).
- **Frontend**: Next.js (Headless UI) consuming the API.
- **Database**: PostgreSQL (Multi-tenant with `django-tenant-schemas`).
- **Infra**: Docker Compose for local development.

## Setup Commands
The project runs fully in Docker. Do not run services on the host machine directly.

- **Start Services**: `make dev` (or `docker compose up -d`).
- **Backend Shell**: `docker exec -it compose-web-1 python manage.py shell`.
- **Run Tests**: `docker exec compose-web-1 pytest`.
- **Frontend Logs**: `docker logs -f compose-frontend-1`.

## Code Style & Conventions
### Backend (Python/Django)
- Follow **PEP 8**.
- Use **Type Hints** everywhere.
- **Serializers**: Use for all API validation (replaces Django Forms).
- **ViewSets**: Prefer `ModelViewSet` or `ViewSet` over function-based views.
- **Tests**: Use `pytest` with fixtures (see `tests/conftest.py`).

### Frontend (TypeScript/Next.js)
- **Framework**: Next.js 14+ (App Router).
- **Styling**: Tailwind CSS + shadcn/ui.
- **State**: Use React Hooks + Context. Avoid Redux unless necessary.
- **i18n**: Use `next-intl`.
- **API**: Use typed `apiPost`, `apiGet` helpers in `src/lib/api.ts`.
- **Components**: Functional components only.

## Architecture Notes
- **Authentication**: JWT/Session handled by Django. Frontend proxies requests via Rewrites (`next.config.ts`).
- **Onboarding**: Flows via `/api/v1/onboarding/` endpoints.
- **Tenancy**: Identified by Header `X-Tenant-ID` or Subdomain.

## Critical Rules
- **Docker First**: Always assume code runs in containers. File paths in tests/commands must match container paths.
- **No HTML Views**: All new "views" must be React pages. Django only serves API JSON.
- **Testing**: Tests must pass inside the container before committing.
