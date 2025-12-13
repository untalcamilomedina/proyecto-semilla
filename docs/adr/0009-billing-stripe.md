# ADR 0009 — Billing con Stripe tenant‑scoped

**Estado:** aceptado  
**Decisión:** Integrar Stripe con servicios puros + webhooks idempotentes. Los webhooks enrutan por metadata `tenant_schema`/`tenant_id`.

**Consecuencias:**

- `StripeEvent` evita re‑procesamiento.  
- `Plan.roles_on_activation` permite mapping plan→roles.

