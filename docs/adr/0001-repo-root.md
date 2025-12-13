# ADR 0001 — Repo root como proyecto

**Estado:** aceptado  
**Contexto:** Este boilerplate pretende ser un “proyecto semilla” fácilmente clonable y extensible.  
**Decisión:** El repositorio raíz contiene directamente el proyecto (no se crea un folder extra `project_slug/`).  
**Consecuencias:**

- Menos pasos al clonar/usar.
- `src/` es el único contenedor de código Python.

