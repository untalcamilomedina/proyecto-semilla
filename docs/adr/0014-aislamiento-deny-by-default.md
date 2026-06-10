# ADR 0014 — Aislamiento multitenant deny-by-default y binding de JWT por schema

**Estado:** aceptado (v0.14.0) · **Fecha:** 2026-06

## Contexto

La auditoría de 2026-06 encontró dos fallos críticos de aislamiento:

1. `PolicyPermission` sin `permission_codename` devolvía `True` para cualquier
   usuario autenticado, sin verificar membresía → un usuario del tenant A podía
   listar miembros (PII) y usar módulos del tenant B.
2. Con usuarios por schema, los IDs colisionan entre tenants. `JWTAuthentication`
   resuelve `user_id` en el schema del host del request → un token emitido para
   el usuario N del tenant A autenticaba como el usuario N del tenant B
   (suplantación de identidad).

## Decisión

1. **Deny-by-default**: toda vista multitenant exige membresía activa.
   `common.api.permissions.IsTenantMember` es el permiso base;
   `PolicyPermission` valida SIEMPRE membresía y, además, los codenames RBAC
   declarados. `IsAuthenticated` a secas queda prohibido en recursos de tenant
   (regla en CLAUDE.md/AGENTS.md).
2. **Binding de JWT**: cada token lleva el claim `schema_name` del schema donde
   se emitió. `TenantJWTAuthentication` rechaza (401) cualquier token usado en
   un schema distinto.

## Consecuencias

- Los invariantes quedan codificados en `tests/test_api_security.py` y
  `tests/test_crm.py`; el CI bloquea cualquier regresión.
- Los tokens emitidos antes de v0.14 no llevan claim y siguen funcionando solo
  en flujos sin tenant (aceptable: no había despliegues productivos).
- Todo módulo nuevo hereda el patrón vía `common.api.tenancy.TenantScopedViewSet`.
