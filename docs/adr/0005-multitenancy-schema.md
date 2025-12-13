# ADR 0005 — Multitenancy por schema (V1)

**Estado:** aceptado  
**Contexto:** Se requiere multitenancy opcional y simple en V1, con aislamiento razonable.  
**Decisión:** Usar Postgres schemas (`public` + schema por tenant) con switching vía `SET search_path`.  
**Consecuencias:**

- `public` es fuente de verdad para routing (`Tenant`, `Domain`).  
- `Tenant` se replica en cada schema para soportar FKs y `request.tenant` local.  
- Preset enterprise DB‑per‑tenant queda como flag futura.

