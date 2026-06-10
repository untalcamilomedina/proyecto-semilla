#!/usr/bin/env python3
"""Servidor MCP de Proyecto Semilla — el arnés agnóstico de modelo.

Expone los "verbos" del proyecto vía Model Context Protocol (stdio), de modo
que CUALQUIER agente compatible (Claude Code, Cursor, Copilot, Gemini CLI,
Codex…) pueda verificar su propio trabajo con las mismas herramientas que el
CI, leer las skills y consultar la documentación — sin depender de un modelo
concreto.

Registro (ya incluido en .mcp.json):
    {"semilla": {"command": "python3", "args": ["scripts/mcp/seed_server.py"]}}

Requiere el SDK oficial: pip install -r requirements/dev.txt  (paquete `mcp`).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = ROOT / ".claude" / "skills"
DOCS_DIR = ROOT / "docs"

# Tope de salida para no inundar el contexto del agente.
MAX_OUTPUT = 12_000

mcp = FastMCP(
    "semilla",
    instructions=(
        "Herramientas de Proyecto Semilla: verifica tu trabajo con los mismos "
        "gates que el CI (lint, typecheck, tests), consulta las skills "
        "(procedimientos del proyecto) y la documentación. Reglas del "
        "proyecto: AGENTS.md."
    ),
)


def _run(cmd: list[str], timeout: int = 600) -> str:
    """Ejecuta un comando del repo y devuelve la cola de su salida."""
    try:
        proc = subprocess.run(  # noqa: S603 — comandos fijos del repo, sin shell
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return f"⏱ Timeout ({timeout}s) ejecutando: {' '.join(cmd)}"
    output = (proc.stdout + "\n" + proc.stderr).strip()
    if len(output) > MAX_OUTPUT:
        output = "…(salida truncada)…\n" + output[-MAX_OUTPUT:]
    status = "✅ OK" if proc.returncode == 0 else f"❌ exit {proc.returncode}"
    return f"{status} — {' '.join(cmd)}\n\n{output}"


@mcp.tool()
def project_status() -> str:
    """Estado del repo: rama, último commit, archivos modificados y guía rápida."""
    branch = _run(["git", "branch", "--show-current"], timeout=10)
    log = _run(["git", "log", "-1", "--format=%h %s"], timeout=10)
    dirty = _run(["git", "status", "--porcelain"], timeout=10)
    n_dirty = len([line for line in dirty.splitlines()[2:] if line.strip()])
    return (
        f"{branch}\n{log}\nArchivos sin commitear: {n_dirty}\n\n"
        "Guía: AGENTS.md · Skills: .claude/skills/ · Docs: docs/ · "
        "Gates: run_lint / run_typecheck / run_backend_tests / run_frontend_tests"
    )


@mcp.tool()
def run_lint() -> str:
    """Lint backend completo (ruff + black + isort + djlint + bandit), igual que CI."""
    return _run(["make", "lint"], timeout=600)


@mcp.tool()
def run_typecheck() -> str:
    """Type-check backend (mypy), igual que CI."""
    return _run(["make", "typecheck"], timeout=600)


@mcp.tool()
def run_backend_tests(path: str = "tests/") -> str:
    """Tests backend con pytest (requiere Postgres/Redis arriba — make dev).

    Args:
        path: archivo o directorio de tests (p. ej. tests/test_api_security.py).
    """
    safe = str((ROOT / path).resolve())
    if not safe.startswith(str(ROOT)):
        return "❌ Ruta fuera del repositorio."
    return _run(
        ["python3", "-m", "pytest", path, "-q", "--no-cov", "-p", "no:cacheprovider"],
        timeout=900,
    )


@mcp.tool()
def run_frontend_tests() -> str:
    """Gates de frontend: eslint + tsc + vitest (igual que CI)."""
    return _run(["make", "frontend-test"], timeout=900)


@mcp.tool()
def list_skills() -> str:
    """Lista las skills del proyecto (procedimientos reutilizables, en español)."""
    if not SKILLS_DIR.exists():
        return "No hay skills instaladas."
    lines = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if skill_file.is_file():
            # Primera línea no vacía tras el título como descripción rápida.
            head = skill_file.read_text(encoding="utf-8").splitlines()
            desc = next((line.strip("# ").strip() for line in head[1:8] if line.strip()), "")
            lines.append(f"- {skill_dir.name}: {desc[:110]}")
    return "Skills disponibles (usa read_skill(nombre)):\n" + "\n".join(lines)


@mcp.tool()
def read_skill(name: str) -> str:
    """Devuelve el contenido completo de una skill por nombre de directorio.

    Args:
        name: nombre del directorio de la skill (ver list_skills).
    """
    skill_file = (SKILLS_DIR / name / "SKILL.md").resolve()
    if not str(skill_file).startswith(str(SKILLS_DIR.resolve())) or not skill_file.is_file():
        return f"❌ Skill '{name}' no encontrada. Usa list_skills."
    return skill_file.read_text(encoding="utf-8")


@mcp.tool()
def read_doc(path: str) -> str:
    """Lee un documento de docs/ (api.md, mcp.md, runbooks/operacion.md, adr/...).

    Args:
        path: ruta relativa dentro de docs/ (p. ej. "api.md" o
            "adr/0014-aislamiento-deny-by-default.md").
    """
    doc = (DOCS_DIR / path).resolve()
    if not str(doc).startswith(str(DOCS_DIR.resolve())) or not doc.is_file():
        available = "\n".join(
            f"- {p.relative_to(DOCS_DIR)}" for p in sorted(DOCS_DIR.rglob("*.md"))
        )
        return f"❌ Documento '{path}' no encontrado. Disponibles:\n{available}"
    return doc.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
