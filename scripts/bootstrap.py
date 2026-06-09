#!/usr/bin/env python3
"""Wizard de instalación de Proyecto Semilla.

De `git clone` a stack corriendo en minutos: configura nombre/branding,
genera las claves criptográficas dedicadas y escribe los archivos de entorno
(local.env + frontend/.env.local). Solo usa stdlib — no requiere instalar nada.

Uso:
    python3 scripts/bootstrap.py            # interactivo
    python3 scripts/bootstrap.py --defaults # sin preguntas (valores por defecto)
    python3 scripts/bootstrap.py --name "Mi SaaS" --slug mi-saas --defaults

Tras el wizard:
    make dev && make migrate && make seed
"""

from __future__ import annotations

import argparse
import re
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MODULES = ["LMS", "COMMUNITY", "MCP", "CRM"]


def _slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "mi-proyecto"


def _ask(prompt: str, default: str, interactive: bool) -> str:
    if not interactive:
        return default
    answer = input(f"{prompt} [{default}]: ").strip()
    return answer or default


def _ask_bool(prompt: str, default: bool, interactive: bool) -> bool:
    if not interactive:
        return default
    suffix = "S/n" if default else "s/N"
    answer = input(f"{prompt} [{suffix}]: ").strip().lower()
    if not answer:
        return default
    return answer in {"s", "si", "sí", "y", "yes"}


def _generate_key() -> str:
    return secrets.token_urlsafe(50)


def build_local_env(config: dict) -> str:
    modules = "\n".join(
        f"ENABLE_{module}={'true' if config['modules'][module] else 'false'}" for module in MODULES
    )
    return f"""# Generado por scripts/bootstrap.py — NO commitear este archivo.
# ── Django ──────────────────────────────────────────────────
DJANGO_SETTINGS_MODULE=config.settings.dev
DJANGO_SECRET_KEY={config['secret_key']}
DEBUG=true
PROJECT_NAME={config['name']}

# Claves dedicadas (independientes del SECRET_KEY para poder rotarlo)
FIELD_ENCRYPTION_KEY={config['field_key']}
JWT_SIGNING_KEY={config['jwt_key']}

# ── Database ────────────────────────────────────────────────
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/{config['db_name']}

# ── Redis / Celery ──────────────────────────────────────────
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# ── MinIO (S3-compatible) ───────────────────────────────────
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=media
S3_ENDPOINT_URL=http://minio:9000

# ── Email (Mailpit) ────────────────────────────────────────
EMAIL_HOST=mailpit
EMAIL_PORT=1025

# ── Frontend ───────────────────────────────────────────────
FRONTEND_URL=http://localhost:{config['frontend_port']}
DOMAIN_BASE={config['domain']}

# ── Módulos opcionales ─────────────────────────────────────
{modules}

# ── Multitenancy ───────────────────────────────────────────
MULTITENANT_MODE=schema

# ── Stripe (vacío en dev; ver production.env.example para prod) ──
# STRIPE_SECRET_KEY=
# STRIPE_WEBHOOK_SECRET=

# ── Observabilidad opcional ────────────────────────────────
# SENTRY_DSN=
# METRICS_TOKEN=
"""


def build_frontend_env(config: dict) -> str:
    return f"""# Generado por scripts/bootstrap.py — NO commitear este archivo.
NEXT_PUBLIC_APP_NAME={config['name']}
NEXT_PUBLIC_APP_URL=http://localhost:{config['frontend_port']}
NEXT_PUBLIC_TENANT_DOMAIN_BASE={config['domain']}
DJANGO_BASE_URL=http://localhost:8000
"""


def build_compose_env(config: dict) -> str:
    """`.env` raíz: variables que docker compose interpola en los YAML
    (POSTGRES_DB, puertos). Sin esto, el nombre de BD del wizard no aplicaría."""
    return f"""# Generado por scripts/bootstrap.py — interpolación de docker compose.
POSTGRES_DB={config['db_name']}
FRONTEND_PORT={config['frontend_port']}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Wizard de instalación de Proyecto Semilla")
    parser.add_argument("--name", help="Nombre del proyecto (branding)")
    parser.add_argument("--slug", help="Slug del proyecto (BD, identificadores)")
    parser.add_argument("--domain", help="Dominio base para tenants (dev: localhost)")
    parser.add_argument("--defaults", action="store_true", help="Sin preguntas: usa defaults/flags")
    parser.add_argument("--force", action="store_true", help="Sobrescribe local.env si ya existe")
    args = parser.parse_args()
    interactive = not args.defaults

    print("🌱 Proyecto Semilla — wizard de instalación\n")

    local_env = ROOT / "local.env"
    if local_env.exists() and not args.force:
        print(f"⚠ {local_env} ya existe. Usa --force para sobrescribir.")
        return 1

    name = args.name or _ask("Nombre del proyecto", "Proyecto Semilla", interactive)
    slug = args.slug or _ask("Slug", _slugify(name), interactive)
    slug = _slugify(slug)
    domain = args.domain or _ask("Dominio base de tenants (dev)", "localhost", interactive)
    frontend_port = _ask("Puerto del frontend", "3010", interactive)

    modules = {}
    print("\nMódulos opcionales (CMS siempre activo):")
    defaults_per_module = {"LMS": True, "COMMUNITY": True, "MCP": True, "CRM": True}
    for module in MODULES:
        modules[module] = _ask_bool(
            f"  ¿Activar {module}?", defaults_per_module[module], interactive
        )

    config = {
        "name": name,
        "slug": slug,
        "db_name": slug.replace("-", "_"),
        "domain": domain,
        "frontend_port": frontend_port,
        "modules": modules,
        "secret_key": _generate_key(),
        "field_key": _generate_key(),
        "jwt_key": _generate_key(),
    }

    local_env.write_text(build_local_env(config), encoding="utf-8")
    print(f"\n✔ {local_env.relative_to(ROOT)} escrito (3 claves únicas generadas).")

    frontend_env = ROOT / "frontend" / ".env.local"
    frontend_env.write_text(build_frontend_env(config), encoding="utf-8")
    print(f"✔ {frontend_env.relative_to(ROOT)} escrito.")

    compose_env = ROOT / ".env"
    compose_env.write_text(build_compose_env(config), encoding="utf-8")
    print(f"✔ {compose_env.relative_to(ROOT)} escrito (interpolación de compose).")

    print(f"""
Siguientes pasos:

  1. make dev          # levanta el stack Docker completo
  2. make migrate      # migraciones (en otra terminal)
  3. make seed         # tenant demo + admin@demo.com/password

  Frontend: http://localhost:{frontend_port} · API docs: http://localhost:8000/api/docs/
  Guía de operación: docs/runbooks/operacion.md · Para agentes IA: CLAUDE.md
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
