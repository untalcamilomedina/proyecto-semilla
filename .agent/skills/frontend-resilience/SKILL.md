---
name: frontend-resilience
description: Agrega error boundaries, loading states, fix navigation i18n, sanitiza stores y corrige middleware stacking
author: Mayordomos Dev Team
version: 1.0.0
---

# Skill: Frontend Resilience para BlockFlow SaaS

Esta skill guia la implementacion de patrones de resiliencia en el frontend Next.js 16: error boundaries, loading states, navegacion i18n correcta, store sanitization y correccion de middleware stacking.

## Prerrequisitos

- [ ] Next.js 16 con App Router y `[locale]` dynamic segment
- [ ] next-intl configurado con `@/lib/navigation` exports
- [ ] Zustand stores con persist middleware
- [ ] openapi-fetch como cliente API

## Cuando Usar

Usar esta skill cuando:
- Faltan `error.tsx`, `loading.tsx` o `not-found.tsx` en route groups
- Componentes usan `next/link` en vez de `@/lib/navigation`
- Zustand stores persisten datos sensibles
- El API client stackea middleware en cada llamada
- No hay Suspense boundaries ni loading states

## Proceso

### Paso 1: Error Boundaries por Route Group

Crear `error.tsx` en cada route group principal.

**Archivos a crear:**
- `frontend/src/app/[locale]/error.tsx`
- `frontend/src/app/[locale]/(dashboard)/error.tsx`
- `frontend/src/app/[locale]/(auth)/error.tsx`

```tsx
// Template: error.tsx (client component)
"use client";

import { useEffect } from "react";
import { GlassButton } from "@/components/ui/glass/GlassButton";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log to error reporting service (Sentry, etc.)
    console.error("Unhandled error:", error);
  }, [error]);

  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4">
      <h2 className="text-xl font-semibold">Something went wrong</h2>
      <p className="text-muted-foreground text-sm">
        {error.digest ? `Error ID: ${error.digest}` : "An unexpected error occurred."}
      </p>
      <GlassButton onClick={reset} variant="outline">
        Try again
      </GlassButton>
    </div>
  );
}
```

### Paso 2: Loading States por Route Group

**Archivos a crear:**
- `frontend/src/app/[locale]/loading.tsx`
- `frontend/src/app/[locale]/(dashboard)/loading.tsx`
- `frontend/src/app/[locale]/(auth)/loading.tsx`

```tsx
// Template: loading.tsx
export default function Loading() {
  return (
    <div className="flex min-h-[50vh] items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>
  );
}
```

### Paso 3: Not Found Pages

**Archivos a crear:**
- `frontend/src/app/[locale]/not-found.tsx`
- `frontend/src/app/[locale]/(dashboard)/not-found.tsx`

```tsx
// Template: not-found.tsx
import { Link } from "@/lib/navigation";

export default function NotFound() {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4">
      <h2 className="text-2xl font-bold">404</h2>
      <p className="text-muted-foreground">Page not found</p>
      <Link href="/dashboard" className="text-primary underline">
        Go to Dashboard
      </Link>
    </div>
  );
}
```

### Paso 4: Fix Navigation Imports (i18n)

**Problema:** La mayoria de archivos importan de `next/link` y `next/navigation` en vez de `@/lib/navigation`, rompiendo el prefijo de locale.

**Archivo de referencia:** `frontend/src/lib/navigation.ts`

**Buscar y reemplazar en estos archivos:**

```typescript
// INCORRECTO - pierde locale prefix:
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";

// CORRECTO - mantiene locale prefix:
import { Link, useRouter, usePathname } from "@/lib/navigation";
```

**Archivos que requieren correccion:**
- `src/components/layout/sidebar.tsx`
- `src/components/diagrams/DiagramsTable.tsx`
- `src/app/[locale]/(dashboard)/dashboard/page.tsx`
- `src/app/[locale]/onboarding/done/page.tsx`
- `src/app/[locale]/(auth)/forgot-password/page.tsx`
- `src/app/[locale]/(auth)/signup/page.tsx`
- `src/app/[locale]/(dashboard)/DashboardClientLayout.tsx`
- Todas las paginas de onboarding

### Paso 5: Fix `<html lang>` Dinamico

**Archivo:** `frontend/src/app/layout.tsx`

```tsx
// ANTES (hardcoded):
<html lang="en">

// DESPUES: Mover el <html> tag al locale layout
// app/layout.tsx solo exporta children sin <html>
// app/[locale]/layout.tsx maneja el <html lang={locale}>
```

**Archivo:** `frontend/src/app/[locale]/layout.tsx`

```tsx
export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;

  return (
    <html lang={locale}>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

export function generateStaticParams() {
  return [{ locale: "en" }, { locale: "es" }];
}
```

### Paso 6: Fix API Client Middleware Stacking

**Archivo:** `frontend/src/lib/api.ts`

**Problema:** `setAuthToken()` agrega un middleware nuevo cada vez sin remover el anterior.

```typescript
// SOLUCION: Usar un token mutable en closure
let _authToken: string | null = null;

// Registrar middleware UNA sola vez
api.use({
  onRequest: ({ request }) => {
    if (_authToken) {
      request.headers.set("Authorization", `Bearer ${_authToken}`);
    }
    return request;
  },
});

// setAuthToken solo actualiza la referencia
export const setAuthToken = (token: string | null) => {
  _authToken = token;
};
```

### Paso 7: Sanitizar Zustand Stores

**Archivo:** `frontend/src/stores/onboarding.ts`

```typescript
// En partialize, EXCLUIR datos sensibles:
partialize: (state) => ({
  organization: state.organization,
  language: state.language,
  step: state.step,
  // User sin password
  user: state.user
    ? { name: state.user.name, email: state.user.email }
    : undefined,
  // Stripe sin secrets
  stripe: state.stripe
    ? { enabled: state.stripe.enabled, publicKey: state.stripe.publicKey }
    : undefined,
}),
```

### Paso 8: Eliminar Archivos Duplicados/Muertos

**Archivos a eliminar:**
```bash
rm "frontend/src/app/[locale]/(dashboard)/members/page 2.tsx"
rm "frontend/src/app/[locale]/onboarding/domain/page 2.tsx"
rm "frontend/src/app/[locale]/onboarding/stripe/page 2.tsx"
rm frontend/src/test_marker
```

**Componentes duplicados a consolidar:**
- `src/components/diagrams/canvas.tsx` vs `canvas/index.tsx` - Mantener `canvas/index.tsx`
- `src/components/diagrams/nodes/entity-node.tsx` vs `ERDEntityNode.tsx` - Consolidar en uno

## Checklist de Verificacion

### Obligatorio
- [ ] `error.tsx` en `[locale]/`, `(dashboard)/`, `(auth)/`
- [ ] `loading.tsx` en `[locale]/`, `(dashboard)/`, `(auth)/`
- [ ] `not-found.tsx` en `[locale]/`, `(dashboard)/`
- [ ] Todos los `Link` importados de `@/lib/navigation`
- [ ] Todos los `useRouter`/`usePathname` de `@/lib/navigation`
- [ ] `<html lang>` usa locale dinamico
- [ ] `generateStaticParams` exportado en `[locale]/layout.tsx`
- [ ] `setAuthToken` no stackea middleware
- [ ] Password excluido de Zustand persist
- [ ] Stripe secrets excluidos de Zustand persist
- [ ] Archivos "page 2.tsx" eliminados
- [ ] `test_marker` eliminado

### Recomendado
- [ ] Migrar `useEffect` data fetching a React Query
- [ ] Reemplazar `alert()`/`confirm()` con dialogs accesibles
- [ ] Agregar `aria-label` a botones interactivos
- [ ] Reemplazar `window.location.reload()` con query invalidation

## Errores Comunes

### Error: "useRouter only works in Client Components"
**Causa:** Importar `useRouter` de `next/navigation` en server component
**Solucion:** Usar `redirect` de `@/lib/navigation` en server components

### Error: 404 al navegar entre paginas
**Causa:** `Link` de `next/link` genera URLs sin locale prefix
**Solucion:** Reemplazar con `Link` de `@/lib/navigation`

### Error: Flash de contenido en paginas protegidas
**Causa:** Auth check es solo client-side via useEffect
**Solucion:** Verificar en middleware.ts que `sessionid` cookie existe (no solo `csrftoken`)

## Referencias

- [Next.js Error Handling](https://nextjs.org/docs/app/building-your-application/routing/error-handling)
- [next-intl Routing](https://next-intl.dev/docs/routing)
- [Zustand Persist Partialize](https://docs.pmnd.rs/zustand/integrations/persisting-store-data)

---

*Ultima actualizacion: 2026-02-05*
