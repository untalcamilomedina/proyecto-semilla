# AGENTS.md

> **Configuración Global para Agentes en este Proyecto (AppNotion)**

## Contexto del Proyecto

Este es un proyecto profesional que funciona como un Marketplace de herramientas SaaS.
El stack base es **Django (Backend)** y **React/Next.js (Frontend)** (Boilerplate Proyecto Semilla).
El objetivo es mantener un código limpio, minimalista, estilo **Glassmorphism Industrial** y libre de deuda técnica.

## Reglas Principales

1.  **Idioma:** Todas las comunicaciones, comentarios y documentación deben estar en **Español**.
2.  **No Suposiciones:** Si falta información, **pregunta** o audita. Nunca inventes soluciones parche.
3.  **Buenas Prácticas:**
    - Uso estricto de **JSDoc** para frontend y **Docstrings** para backend.
    - Componentes tipados fuertemente con **TypeScript** (si aplica).
    - Arquitectura modular (Backend: Apps Django, Frontend: Atomic/Feature).
4.  **Estilo de Código:**
    - Seguir las reglas de `ESLint`, `Prettier` (JS) y `Black`/`Flake8` (Python).
    - Nombres de variables en inglés, comentarios en español.

## Comandos Útiles (Referencia General)

- **Frontend:** Revisar `frontend/package.json`.
- **Backend:** `python manage.py runserver`.
- **Docker:** El proyecto usa Docker (`Dockerfile`, `compose/`).

## Flujo de Trabajo

1.  Planificar cambios en `implementation_plan.md`.
2.  Pedir revisión al usuario.
3.  Implementar cambios auditablemente.
4.  Verificar con tests o pruebas manuales documentadas.
