# ADR 0002 — Tooling y calidad

**Estado:** aceptado  
**Decisión:** Se usan `ruff`, `black`, `isort`, `bandit`, `djlint`, `mypy` y `pytest` con pre‑commit como fuente de verdad. Dependencias en `requirements/` para compatibilidad simple.

**Consecuencias:**

- CI y local comparten exactamente las mismas reglas.
- Cobertura mínima 90% en CI.

