#!/usr/bin/env python3
"""Wizard de instalación de Proyecto Semilla.

Instalación guiada al estilo de los instaladores de WordPress/Mautic/cal.com:
comprobación de requisitos, preguntas con validación, resumen con confirmación
y arranque opcional del stack. Solo stdlib — no requiere instalar nada.

Uso:
    python3 scripts/bootstrap.py            # interactivo (recomendado)
    python3 scripts/bootstrap.py --defaults # sin preguntas (CI/automatización)
    python3 scripts/bootstrap.py --name "Mi SaaS" --slug mi-saas --defaults

Tras el wizard:
    make dev && make migrate && make seed
"""

from __future__ import annotations

import argparse
import re
import secrets
import shutil
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MODULES = {
    "LMS": "Cursos y certificados (Learning Management)",
    "COMMUNITY": "Foros y comunidad estilo Skool",
    "MCP": "Catálogo de tools para agentes de IA",
    "CRM": "Empresas, contactos y pipeline de ventas",
}

_USE_COLOR = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text


def ok(text: str) -> str:
    return _c("32", text)


def warn(text: str) -> str:
    return _c("33", text)


def bold(text: str) -> str:
    return _c("1", text)


def dim(text: str) -> str:
    return _c("2", text)


def _slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "mi-proyecto"


def _ask(prompt: str, default: str, interactive: bool, validate=None) -> str:
    if not interactive:
        return default
    while True:
        answer = input(f"  {prompt} {dim(f'[{default}]')}: ").strip() or default
        if validate is None:
            return answer
        error = validate(answer)
        if error is None:
            return answer
        print(f"  {warn('✗')} {error}")


def _ask_bool(prompt: str, default: bool, interactive: bool) -> bool:
    if not interactive:
        return default
    suffix = "S/n" if default else "s/N"
    answer = input(f"  {prompt} {dim(f'[{suffix}]')}: ").strip().lower()
    if not answer:
        return default
    return answer in {"s", "si", "sí", "y", "yes"}


def _validate_port(value: str) -> str | None:
    if not value.isdigit() or not (1 <= int(value) <= 65535):
        return "Debe ser un número de puerto válido (1-65535)."
    return None


def _validate_domain(value: str) -> str | None:
    if not re.fullmatch(r"[a-z0-9.-]+", value):
        return "Solo minúsculas, números, puntos y guiones (ej. localhost, miapp.dev)."
    return None


def _port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.3)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _generate_key() -> str:
    return secrets.token_urlsafe(50)


def preflight() -> list[tuple[str, bool, str]]:
    """Comprobación de requisitos (estilo instalador de Mautic)."""
    checks: list[tuple[str, bool, str]] = []
    checks.append(
        (
            "Python 3.10+",
            sys.version_info >= (3, 10),
            f"detectado {sys.version_info.major}.{sys.version_info.minor}",
        )
    )
    docker = shutil.which("docker") is not None
    checks.append(
        ("Docker CLI", docker, "instala Docker Desktop o docker-ce" if not docker else "")
    )
    compose_ok = False
    if docker:
        try:
            compose_ok = (
                subprocess.run(
                    ["docker", "compose", "version"], capture_output=True, timeout=10
                ).returncode
                == 0
            )
        except Exception:
            compose_ok = False
    checks.append(
        ("Docker Compose v2", compose_ok, "incluido en Docker Desktop" if not compose_ok else "")
    )
    return checks


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
    parser.add_argument(
        "--defaults", "--yes", action="store_true", help="Sin preguntas: usa defaults/flags"
    )
    parser.add_argument("--force", action="store_true", help="Sobrescribe local.env si ya existe")
    args = parser.parse_args()
    interactive = not args.defaults

    print()
    print(bold("  🌱 Proyecto Semilla — instalación guiada"))
    print(dim("  Boilerplate SaaS multitenant, seguro y AI-first"))
    print(dim("  ────────────────────────────────────────────────"))

    # Paso 1/4: requisitos
    print(f"\n{bold('  Paso 1/4 · Requisitos')}")
    all_ok = True
    for label, passed, hint in preflight():
        mark = ok("✔") if passed else warn("✗")
        extra = dim(f" — {hint}") if hint else ""
        print(f"   {mark} {label}{extra}")
        if not passed and label != "Python 3.10+":
            all_ok = False
    if not all_ok:
        print(f"\n  {warn('Docker no está disponible.')} Puedes continuar (se generan los")
        print("  archivos de entorno) pero necesitarás Docker para `make dev`.")
        if interactive and not _ask_bool("¿Continuar de todos modos?", True, interactive):
            return 1

    local_env = ROOT / "local.env"
    if local_env.exists() and not args.force:
        print(f"\n  {warn('⚠')} {local_env.name} ya existe. Usa --force para sobrescribir.")
        return 1

    # Paso 2/4: identidad y módulos
    print(f"\n{bold('  Paso 2/4 · Tu proyecto')}")
    name = args.name or _ask("Nombre del proyecto", "Proyecto Semilla", interactive)
    slug = _slugify(args.slug or _ask("Slug", _slugify(name), interactive))
    domain = args.domain or _ask(
        "Dominio base de tenants (dev)", "localhost", interactive, validate=_validate_domain
    )
    frontend_port = _ask("Puerto del frontend", "3010", interactive, validate=_validate_port)
    if _port_in_use(int(frontend_port)):
        print(
            f"   {warn('⚠')} El puerto {frontend_port} parece ocupado — recuerda liberarlo o cambiarlo."
        )

    print(f"\n{bold('  Paso 3/4 · Módulos opcionales')} {dim('(CMS siempre activo)')}")
    modules = {}
    for module, description in MODULES.items():
        modules[module] = _ask_bool(f"{module} — {dim(description)}", True, interactive)

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

    # Paso 4/4: resumen y confirmación (estilo cal.com)
    actives = ", ".join(m for m, on in modules.items() if on) or "ninguno"
    slug_info = dim(f"(slug: {slug} · BD: {config['db_name']})")
    print(f"\n{bold('  Paso 4/4 · Resumen')}")
    print(f"   Proyecto   {bold(name)}  {slug_info}")
    print(f"   Dominio    {domain}  ·  Frontend  http://localhost:{frontend_port}")
    print(f"   Módulos    CMS + {actives}")
    print(f"   Claves     3 claves criptográficas únicas {dim('(SECRET/cifrado/JWT)')}")
    print(f"   Archivos   local.env · frontend/.env.local · .env")
    if interactive and not _ask_bool("¿Escribir la configuración?", True, interactive):
        print("  Cancelado. No se escribió nada.")
        return 1

    local_env.write_text(build_local_env(config), encoding="utf-8")
    (ROOT / "frontend" / ".env.local").write_text(build_frontend_env(config), encoding="utf-8")
    (ROOT / ".env").write_text(build_compose_env(config), encoding="utf-8")
    print(f"\n  {ok('✔')} Configuración escrita.")

    # Arranque opcional del stack (instalación en un paso, estilo WordPress)
    if (
        interactive
        and all_ok
        and _ask_bool("¿Levantar el stack ahora? (make dev)", False, interactive)
    ):
        print(dim("\n  Lanzando docker compose — Ctrl+C para detener.\n"))
        subprocess.call(["make", "dev"], cwd=ROOT)
        return 0

    print(f"""
  {bold('Siguientes pasos:')}

    1. make dev          {dim('# levanta el stack Docker completo')}
    2. make migrate      {dim('# migraciones (en otra terminal)')}
    3. make seed         {dim('# tenant demo + admin@demo.com/password')}

  Frontend  http://localhost:{frontend_port}  ·  API docs  http://localhost:8000/api/docs/
  Operación: docs/runbooks/operacion.md  ·  Agentes IA: CLAUDE.md
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
