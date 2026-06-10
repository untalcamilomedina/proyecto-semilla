# Guía de contribución

¡Gracias por tu interés en contribuir a **Proyecto Semilla**! 🌱

Este repositorio es un **boilerplate SaaS genérico** (Django 5 + DRF + Next.js 16, multitenant y AI-first). Las contribuciones deben mejorar la base para *cualquier* producto derivado: la lógica de producto concreta vive en repos derivados, no aquí.

> El idioma del proyecto es el **español** (docs, commits, comentarios); los identificadores de código van en inglés.

## Índice

1. [Antes de empezar](#antes-de-empezar)
2. [Levantar el entorno de desarrollo](#levantar-el-entorno-de-desarrollo)
3. [Estándares de calidad](#estándares-de-calidad)
4. [Flujo de Pull Request](#flujo-de-pull-request)
5. [Reglas para agentes de IA](#reglas-para-agentes-de-ia)
6. [Proponer módulos nuevos](#proponer-módulos-nuevos)
7. [Reportar bugs y vulnerabilidades](#reportar-bugs-y-vulnerabilidades)
8. [Código de conducta](#código-de-conducta)

## Antes de empezar

- Revisa los [issues abiertos](https://github.com/untalcamilomedina/proyecto-semilla/issues) para no duplicar trabajo.
- Para ideas o dudas, usa [Discussions](https://github.com/untalcamilomedina/proyecto-semilla/discussions) antes de abrir un issue.
- Para cambios grandes (módulos nuevos, cambios de arquitectura), abre primero un issue o discusión para alinear el enfoque y evitar trabajo desperdiciado.

## Levantar el entorno de desarrollo

Requisitos: Docker + Docker Compose, Python 3.12+, Node 20+.

```bash
make init      # bootstrap del proyecto (genera config local desde local.env.example)
make dev       # levanta el stack Docker: web :8000, frontend :3010, postgres, redis, minio, mailpit
make migrate   # aplica migraciones en el schema public
make seed      # carga datos demo (tenant, usuarios, roles)
```

Para el frontend en modo standalone:

```bash
cd frontend && npm install && npm run dev
```

Detalles adicionales en [`README.md`](./README.md) y en los runbooks de [`docs/runbooks/`](./docs/runbooks/).

## Estándares de calidad

Todo PR debe pasar **obligatoriamente** estos checks (la CI los ejecuta, pero córrelos en local antes):

```bash
make lint        # ruff + black + isort + djlint + bandit
make typecheck   # mypy
make test        # pytest — REQUIERE Postgres (córrelo dentro de Docker o con servicios arriba)
cd frontend && npm run lint && npm run type-check && npm run test   # si tocaste frontend
```

> Los tests del backend no soportan SQLite. Dentro de Docker:
> `docker compose -f compose/docker-compose.yml exec web pytest tests/`

Además:

- **Commits convencionales en español**: `feat: añade exportación CSV de miembros`, `fix: corrige scoping de tenant en invitaciones`, `docs: ...`, `chore: ...`, `refactor: ...`, `test: ...`.
- **Una migración por cambio de modelo**: cada cambio de modelos incluye su migración nueva. Nunca edites una migración ya commiteada; crea una nueva.
- **Seguridad multitenant**: los viewsets de recursos de tenant usan `IsTenantMember`/`PolicyPermission` y querysets scoped por tenant (`common.api.tenancy`). Nunca `IsAuthenticated` a secas.
- **Serializers DRF** con lista explícita de `fields` (nunca `__all__` en modelos con datos sensibles).
- **i18n**: toda string visible del frontend pasa por `useTranslations` y se añade a `messages/{es,en,pt}.json` (los tres idiomas).
- **Secretos solo por variables de entorno** (`environs`); nunca hardcodeados ni commiteados.
- **Dependencias**: si añades una, actualiza `requirements/*.txt` (backend) o `package.json` + lockfile (frontend).
- No edites a mano `frontend/src/types/api.ts` (se genera con `npm run generate-sdk`).

## Flujo de Pull Request

1. Haz fork (o crea una rama si tienes acceso) **desde `main`**: `git checkout -b feat/mi-cambio main`.
2. Desarrolla en commits pequeños y atómicos, con mensajes convencionales en español.
3. Ejecuta los checks locales (`make lint`, `make typecheck`, `make test`, y los del frontend si aplica).
4. Abre el PR completando la [plantilla](./.github/PULL_REQUEST_TEMPLATE.md): qué cambia, por qué y cómo se probó. Enlaza el issue relacionado (`Closes #123`).
5. La **CI debe estar en verde**: no se desactivan checks para que pase; se arregla la causa.
6. Se requiere la aprobación de **un revisor** (las rutas sensibles tienen revisión obligatoria del maintainer vía [CODEOWNERS](./.github/CODEOWNERS)).
7. Atiende el feedback con commits adicionales; el merge lo realiza el maintainer.

## Reglas para agentes de IA

Si contribuyes usando agentes de IA (Claude Code, Cursor, Copilot, etc.), las reglas del proyecto para agentes están en [`AGENTS.md`](./AGENTS.md), que apunta a la guía canónica [`CLAUDE.md`](./CLAUDE.md): arquitectura, reglas de seguridad no negociables, convenciones y catálogo de skills. Eres responsable de revisar y entender todo el código generado que envíes en un PR.

## Proponer módulos nuevos

Los módulos opcionales (como `cms`, `lms`, `community`, `crm`) se activan por feature flag y siguen una estructura estándar. Antes de proponer uno:

1. Abre un issue/discusión explicando el caso de uso genérico (recuerda: nada de lógica de producto en la semilla).
2. Usa la skill **`scaffold-full-stack-feature`** (en [`.claude/skills/`](./.claude/skills/)) para generar el vertical slice completo (modelo → servicio → API → frontend) siguiendo las convenciones del proyecto.
3. Incluye: feature flag en env, tests de API (auth, permisos, scoping por tenant), i18n en los tres idiomas y documentación.

## Reportar bugs y vulnerabilidades

- **Bugs**: usa el [formulario de bug report](https://github.com/untalcamilomedina/proyecto-semilla/issues/new/choose).
- **Vulnerabilidades de seguridad**: **NO abras un issue público.** Repórtalas de forma privada mediante [GitHub Security Advisories](https://github.com/untalcamilomedina/proyecto-semilla/security/advisories/new). Más detalles en [`SECURITY.md`](./SECURITY.md).

## Código de conducta

Este proyecto se rige por el [Código de Conducta](./CODE_OF_CONDUCT.md). Al participar, te comprometes a mantener un ambiente respetuoso e inclusivo. Reporta comportamientos inaceptables a través de los canales indicados en ese documento.

---

Proyecto Semilla se distribuye bajo licencia [MIT](./LICENSE). Al contribuir, aceptas que tu código se publique bajo la misma licencia.
