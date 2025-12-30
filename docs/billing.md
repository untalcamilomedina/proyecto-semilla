# Billing (Stripe)
## Table of Contents
1. [Modelo](#modelo)
2. [Webhooks](#webhooks)
## Modelo

- `Plan`, `Price`, `Subscription`, `Invoice`.
- `StripeEvent` asegura idempotencia de webhooks.

## Webhooks

Endpoint: `POST /billing/webhooks/stripe/`.

Eventos soportados:

- `checkout.session.completed`
- `customer.subscription.updated/deleted`
- `invoice.payment_succeeded/failed`

Los webhooks enrután por `metadata.tenant_schema` y `metadata.tenant_id`.

