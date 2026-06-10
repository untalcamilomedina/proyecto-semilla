# Pull Request

> Las reglas del proyecto (seguridad, multitenancy, i18n, convenciones) viven en
> [`CLAUDE.md`](../CLAUDE.md) y [`AGENTS.md`](../AGENTS.md). Léelas antes de abrir el PR.

## ¿Qué cambia y por qué?

<!--
Describe el cambio y la motivación. Si resuelve un issue, enlázalo: "Closes #123".
Incluye capturas de pantalla si hay cambios visuales.
-->

## ¿Cómo se probó?

Marca lo que aplique a tu cambio (los checks de CI deben pasar igualmente):

- [ ] `make lint` (ruff + black + isort + djlint + bandit)
- [ ] `make typecheck` (mypy)
- [ ] `make test` (pytest — requiere Postgres, p. ej. dentro de Docker)
- [ ] `make frontend-test` / `cd frontend && npm run lint && npm run type-check` (si toqué frontend)
- [ ] Probado manualmente con `make dev` (describe el flujo arriba)

## Checklist

- [ ] Si cambié modelos, incluí las **migraciones nuevas** (nunca edité una migración ya commiteada).
- [ ] Si toqué strings visibles del frontend, añadí las claves de **i18n en los 3 idiomas** (`messages/{es,en,pt}.json`).
- [ ] Si el cambio es user-facing, actualicé **`CHANGELOG.md`**.
- [ ] No incluyo **secretos**, credenciales ni datos sensibles (config solo por variables de entorno).
- [ ] Los endpoints de tenant usan `IsTenantMember`/`PolicyPermission` y el queryset está scoped por tenant.
- [ ] Los commits siguen el formato convencional y están escritos en español.
