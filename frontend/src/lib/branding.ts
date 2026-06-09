/**
 * Branding central del proyecto.
 *
 * Personaliza tu producto aquí (o vía variables NEXT_PUBLIC_*): el resto del
 * frontend importa estos valores en lugar de hardcodear marca/URLs.
 */

export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || "Proyecto Semilla";

export const APP_TAGLINE =
  process.env.NEXT_PUBLIC_APP_TAGLINE || "Boilerplate SaaS multitenant, seguro y AI-first";

export const APP_DESCRIPTION =
  process.env.NEXT_PUBLIC_APP_DESCRIPTION ||
  "Base SaaS con Django + Next.js: multitenancy, RBAC, billing con Stripe y desarrollo asistido por IA.";

export const APP_URL = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";

/** Dominio base para subdominios de tenants (solo display; el backend manda). */
export const TENANT_DOMAIN_BASE = process.env.NEXT_PUBLIC_TENANT_DOMAIN_BASE || "localhost";
