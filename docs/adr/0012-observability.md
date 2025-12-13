# ADR 0012 — Observabilidad mínima V1

**Estado:** aceptado  
**Decisión:** Exponer `/healthz`, `/readyz`, `/metrics` y Sentry opcional auto‑init.  

**Consecuencias:**

- Fly.io y Kubernetes pueden usar readiness/liveness.  
- Prometheus scrape estándar.  
- Sentry no rompe dev si `SENTRY_DSN` vacío.

