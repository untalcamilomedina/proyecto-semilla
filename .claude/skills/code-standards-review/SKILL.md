---
name: code-standards-review
description: Audita codigo nuevo/modificado contra los estandares del proyecto BlockFlow (tema, i18n, a11y, navegacion, seguridad).
author: BlockFlow Dev Team
version: 1.0.0
---

# Skill: Code Standards Review

Audita archivos `.tsx`/`.ts` del frontend contra los estándares de calidad del proyecto BlockFlow. Diseñado para ejecutarse antes de commits o al revisar PRs.

## Cuándo Usar

- Antes de hacer commit de código nuevo o modificado
- Al revisar pull requests
- Después de crear componentes o páginas nuevas
- Para auditar código existente

## Checklist de Estándares

### 1. Sistema de Temas (Zero Hardcoding)

**PROHIBIDO** usar colores hardcodeados en archivos `.tsx`. Buscar y reportar:

```
# Colores de fondo prohibidos
bg-white/*, bg-black/*, bg-zinc-*, bg-gray-*, bg-slate-*

# Colores de texto prohibidos
text-white, text-white/*, text-zinc-*, text-gray-*, text-slate-*

# Bordes prohibidos
border-white/*, border-zinc-*, border-gray-*

# Sombras prohibidas
shadow-[0_0_*rgba(13,242,13*]
```

**REQUERIDO** usar tokens semánticos:

| Categoría | Tokens Permitidos |
|---|---|
| **Fondos** | `bg-background`, `bg-glass-bg`, `bg-glass-bg-hover`, `bg-glass-bg-strong`, `bg-glass-overlay`, `bg-glass-overlay-strong`, `bg-surface-page`, `bg-surface-raised`, `bg-surface-overlay`, `bg-card`, `bg-muted`, `bg-popover`, `bg-sidebar` |
| **Texto** | `text-foreground`, `text-text-highlight`, `text-text-subtle`, `text-text-secondary`, `text-text-tertiary`, `text-text-quaternary`, `text-text-ghost`, `text-muted-foreground`, `text-card-foreground` |
| **Bordes** | `border-border`, `border-glass-border`, `border-glass-border-subtle`, `border-input` |
| **Brand** | `text-neon-text`, `bg-neon-bg`, `bg-neon-bg-strong`, `border-neon-border`, `shadow-neon` |
| **Error** | `text-error-text`, `bg-error-bg`, `border-error-border` |
| **Status** | `text-success-text`, `text-warning-text`, `bg-warning-bg`, `border-warning-border` |
| **Gradientes** | `text-gradient-heading`, `text-gradient-heading-r` |

**Excepciones aceptables**:
- Colores de feature/marca con opacity: `bg-blue-500/10`, `text-blue-400`, `bg-purple-500/10`, `text-purple-400`, Miro brand colors
- `text-white` SOLO sobre fondos de color sólido para contraste (ej. `bg-destructive text-white`, `bg-purple-500 text-white`)
- Componentes shadcn/ui base (`button.tsx`, `card.tsx`, `input.tsx`, `badge.tsx`, `dialog.tsx`) deben usar tokens de shadcn (`bg-primary`, `text-primary-foreground`, `bg-card`, `border-input`, `bg-accent`, etc.)

### 2. Internacionalización (i18n)

**PROHIBIDO**:
- Strings de UI hardcodeados en español o inglés en componentes `.tsx`
- Usar `t()` sin namespace definido

**REQUERIDO**:
- `useTranslations("namespace")` para todo texto visible
- Keys existentes en `messages/en.json` Y `messages/es.json`
- Usar `@/lib/navigation` para Link, useRouter, usePathname (NO `next/link` ni `next/navigation`)

**Excepciones**: `redirect()` de `next/navigation` para redirects del mismo locale, `useParams()` de `next/navigation`.

### 3. Accesibilidad (a11y - WCAG 2.1 AA)

**REQUERIDO**:
- Todo `<input>` debe tener `<label htmlFor={id}>` asociado (usar `React.useId()` si no hay id explícito)
- Todo botón de ícono debe tener `aria-label`
- Todo formulario debe tener mensajes de error vinculados
- Spinners deben tener `role="status"` y texto `sr-only`
- Navegación por teclado funcional
- No usar `alert()` ni `confirm()` nativos (usar dialogs accesibles)

### 4. Navegación

**REQUERIDO**:
- Imports de `Link`, `useRouter`, `usePathname` desde `@/lib/navigation`
- `redirect` desde `next/navigation` (NOT from `@/lib/navigation` — it expects objects)
- `useParams` desde `next/navigation`

### 5. Seguridad

**PROHIBIDO**:
- Secrets o API keys en código client-side
- `dangerouslySetInnerHTML` sin sanitización
- `eval()` o `new Function()`
- `window.location.reload()` (usar router)

**REQUERIDO**:
- Guard `request.tenant` con `getattr(request, "tenant", None)` en backend
- No incluir passwords ni secret keys en Zustand `partialize`

### 6. Rendimiento

**RECOMENDADO**:
- `useTranslations` con namespace específico (no cargar todo)
- Lazy loading para componentes pesados (`dynamic()`)
- Imágenes con `next/image` y dimensiones definidas
- No `useEffect` para data fetching (preferir React Query / TanStack Query)

## Proceso de Auditoría

1. **Listar archivos modificados**: `git diff --name-only` o archivos proporcionados
2. **Para cada archivo `.tsx`**:
   a. Grep por patrones prohibidos de tema
   b. Grep por strings hardcodeados (textos en español/inglés fuera de `t()`)
   c. Verificar imports de navegación
   d. Verificar labels y aria-labels
   e. Verificar seguridad
3. **Generar reporte** con formato:
   ```
   ## [archivo.tsx]
   - ❌ TEMA: `text-white/50` en línea 23 -> usar `text-text-secondary`
   - ❌ I18N: "Save Changes" hardcodeado en línea 45 -> usar t("save")
   - ✅ A11Y: Labels correctos
   - ✅ NAV: Imports correctos
   ```

## Comando de Verificación Rápida

Para verificar colores hardcodeados en archivos `.tsx`:

```bash
grep -rn --include="*.tsx" -E "(text-white|bg-white/|border-white/|bg-zinc-|text-zinc-|bg-black/|text-gray-|border-gray-)" frontend/src/
```

Para verificar imports de navegación incorrectos:
```bash
grep -rn --include="*.tsx" "from ['\"]next/link['\"]" frontend/src/
grep -rn --include="*.tsx" "from ['\"]next/navigation['\"]" frontend/src/ | grep -v "redirect\|useParams"
```
