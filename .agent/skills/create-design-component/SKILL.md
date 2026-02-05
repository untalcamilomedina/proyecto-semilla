---
name: create-design-component
description: Guía para crear componentes UI siguiendo el Design System "Glass Minimalist" con a11y e i18n.
author: AppNotion Design Team
version: 2.0.0
---

# Skill: Crear Componente de Diseño

Esta skill estandariza la creación de componentes visuales bajo la estética "Glass Minimalist" del proyecto, asegurando accesibilidad (WCAG 2.1 AA) e internacionalización.

## Principios de Diseño

| Principio | Descripción | Implementación |
|-----------|-------------|----------------|
| **Mobile First** | Diseñar para móvil, escalar a desktop | `w-full` → `md:w-auto` |
| **Glassmorphism** | Fondos translúcidos, bordes sutiles | `bg-white/5`, `backdrop-blur-md` |
| **Monocromático** | Escala de grises, acentos mínimos | `zinc-50` a `zinc-950` |
| **Accesible** | WCAG 2.1 AA, keyboard-friendly | `focus-visible`, `aria-*` |
| **i18n-Ready** | Sin textos hardcodeados | `useTranslations()` |

## Prerrequisitos

- [ ] Tailwind CSS configurado.
- [ ] Conocer el tipo de componente (Atom, Molecule, Organism).
- [ ] Tener namespace i18n si el componente tiene texto.

## Arquitectura de Componentes

```
frontend/src/components/
├── ui/                        # Átomos (primitivos)
│   ├── button.tsx
│   ├── input.tsx
│   ├── glass/                 # Variantes Glass
│   │   ├── GlassCard.tsx
│   │   ├── GlassButton.tsx
│   │   └── GlassModal.tsx
│   └── ...
├── layout/                    # Estructura (Sidebar, Header)
│   └── sidebar.tsx
├── members/                   # Moléculas por feature
│   ├── members-table.tsx
│   └── invite-member-modal.tsx
└── onboarding/                # Flujos complejos
    └── WizardLayout.tsx
```

## Proceso

### Paso 1: Clasificar el Componente

| Tipo | Descripción | Ejemplos | Ubicación |
|------|-------------|----------|-----------|
| **Atom** | Elemento único, sin lógica | Button, Input, Badge | `ui/` |
| **Molecule** | Combinación de átomos | SearchInput, Card con acciones | `ui/` o feature |
| **Organism** | Sección completa | MembersTable, InviteModal | `[feature]/` |

### Paso 2: Elegir Variante Base

---

## Templates de Componentes

### Template A: Glass Card

**Archivo:** `frontend/src/components/ui/glass/GlassCard.tsx`

```tsx
import { cn } from "@/lib/utils";
import { forwardRef } from "react";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: "glass" | "solid" | "elevated";
    padding?: "none" | "sm" | "md" | "lg";
}

export const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
    ({ className, variant = "glass", padding = "md", children, ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn(
                    // Base
                    "rounded-2xl transition-all duration-300",
                    // Padding variants
                    {
                        "p-0": padding === "none",
                        "p-4": padding === "sm",
                        "p-6": padding === "md",
                        "p-8": padding === "lg",
                    },
                    // Style variants
                    variant === "glass" && [
                        "bg-white/5 dark:bg-black/20",
                        "backdrop-blur-md",
                        "border border-white/10 dark:border-white/5",
                    ],
                    variant === "solid" && [
                        "bg-zinc-900/80",
                        "border border-zinc-800",
                    ],
                    variant === "elevated" && [
                        "bg-white/5",
                        "backdrop-blur-xl",
                        "border border-white/10",
                        "shadow-2xl shadow-black/20",
                    ],
                    className
                )}
                {...props}
            >
                {children}
            </div>
        );
    }
);

GlassCard.displayName = "GlassCard";
```

### Template B: Glass Button

**Archivo:** `frontend/src/components/ui/glass/GlassButton.tsx`

```tsx
import { cn } from "@/lib/utils";
import { forwardRef } from "react";
import { Loader2 } from "lucide-react";

interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "default" | "ghost" | "destructive";
    size?: "sm" | "md" | "lg";
    loading?: boolean;
}

export const GlassButton = forwardRef<HTMLButtonElement, GlassButtonProps>(
    ({ className, variant = "default", size = "md", loading, disabled, children, ...props }, ref) => {
        return (
            <button
                ref={ref}
                disabled={disabled || loading}
                className={cn(
                    // Base
                    "inline-flex items-center justify-center rounded-xl",
                    "font-medium transition-all duration-200",
                    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/20",
                    "disabled:opacity-50 disabled:cursor-not-allowed",
                    // Size variants
                    {
                        "h-9 px-4 text-sm": size === "sm",
                        "h-11 px-6 text-sm": size === "md",
                        "h-12 px-8 text-base": size === "lg",
                    },
                    // Style variants
                    variant === "default" && [
                        "bg-white/10 hover:bg-white/15",
                        "border border-white/10 hover:border-white/20",
                        "text-white",
                        "active:scale-[0.98]",
                    ],
                    variant === "ghost" && [
                        "hover:bg-white/5",
                        "text-white/70 hover:text-white",
                    ],
                    variant === "destructive" && [
                        "bg-red-500/10 hover:bg-red-500/20",
                        "border border-red-500/20",
                        "text-red-400",
                    ],
                    className
                )}
                {...props}
            >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />}
                {children}
            </button>
        );
    }
);

GlassButton.displayName = "GlassButton";
```

### Template C: Glass Input

**Archivo:** `frontend/src/components/ui/glass/GlassInput.tsx`

```tsx
import { cn } from "@/lib/utils";
import { forwardRef } from "react";

interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    error?: boolean;
    icon?: React.ReactNode;
}

export const GlassInput = forwardRef<HTMLInputElement, GlassInputProps>(
    ({ className, error, icon, ...props }, ref) => {
        return (
            <div className="relative">
                {icon && (
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" aria-hidden="true">
                        {icon}
                    </div>
                )}
                <input
                    ref={ref}
                    className={cn(
                        // Base - Mobile First (44px touch target)
                        "w-full h-11 rounded-xl px-4",
                        "bg-white/5 backdrop-blur-sm",
                        "border border-white/10",
                        "text-white placeholder:text-white/30",
                        "transition-all duration-200",
                        // Focus states
                        "focus:outline-none focus:ring-2 focus:ring-white/20",
                        "focus:border-white/20",
                        // Error state
                        error && "border-red-500/50 focus:ring-red-500/20",
                        // With icon
                        icon && "pl-10",
                        className
                    )}
                    aria-invalid={error ? "true" : undefined}
                    {...props}
                />
            </div>
        );
    }
);

GlassInput.displayName = "GlassInput";
```

### Template D: Glass Modal

**Archivo:** `frontend/src/components/ui/glass/GlassModal.tsx`

```tsx
"use client";

import { cn } from "@/lib/utils";
import { X } from "lucide-react";
import { useTranslations } from "next-intl";
import { useEffect, useRef } from "react";

interface GlassModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    title: string;
    description?: string;
    children: React.ReactNode;
    className?: string;
}

export function GlassModal({
    open,
    onOpenChange,
    title,
    description,
    children,
    className,
}: GlassModalProps) {
    const t = useTranslations("common");
    const modalRef = useRef<HTMLDivElement>(null);
    const previousActiveElement = useRef<HTMLElement | null>(null);

    // Focus management
    useEffect(() => {
        if (open) {
            previousActiveElement.current = document.activeElement as HTMLElement;
            modalRef.current?.focus();
        } else {
            previousActiveElement.current?.focus();
        }
    }, [open]);

    // Escape key handler
    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === "Escape" && open) {
                onOpenChange(false);
            }
        };
        document.addEventListener("keydown", handleEscape);
        return () => document.removeEventListener("keydown", handleEscape);
    }, [open, onOpenChange]);

    if (!open) return null;

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
            aria-describedby={description ? "modal-description" : undefined}
        >
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
                onClick={() => onOpenChange(false)}
                aria-hidden="true"
            />

            {/* Modal Content */}
            <div
                ref={modalRef}
                tabIndex={-1}
                className={cn(
                    "relative w-full max-w-lg",
                    "bg-zinc-900/90 backdrop-blur-xl",
                    "border border-white/10 rounded-2xl",
                    "shadow-2xl shadow-black/40",
                    "p-6",
                    "animate-in fade-in zoom-in-95 duration-200",
                    className
                )}
            >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                    <div>
                        <h2 id="modal-title" className="text-lg font-semibold text-white">
                            {title}
                        </h2>
                        {description && (
                            <p id="modal-description" className="text-sm text-white/50 mt-1">
                                {description}
                            </p>
                        )}
                    </div>
                    <button
                        onClick={() => onOpenChange(false)}
                        className="p-2 rounded-lg hover:bg-white/5 transition-colors"
                        aria-label={t("close")}
                    >
                        <X className="h-5 w-5 text-white/50" aria-hidden="true" />
                    </button>
                </div>

                {/* Body */}
                {children}
            </div>
        </div>
    );
}
```

### Template E: Componente con i18n

**Patrón para componentes que muestran texto:**

```tsx
"use client";

import { useTranslations } from "next-intl";

interface EmptyStateProps {
    namespace?: string;
    icon?: React.ReactNode;
    action?: React.ReactNode;
}

export function EmptyState({ namespace = "common", icon, action }: EmptyStateProps) {
    const t = useTranslations(namespace);

    return (
        <div
            className="flex flex-col items-center justify-center py-12 text-center"
            role="status"
            aria-label={t("empty.title")}
        >
            {icon && (
                <div className="mb-4 text-white/20" aria-hidden="true">
                    {icon}
                </div>
            )}
            <h3 className="text-lg font-medium text-white/70">
                {t("empty.title")}
            </h3>
            <p className="text-sm text-white/40 mt-1 max-w-sm">
                {t("empty.description")}
            </p>
            {action && <div className="mt-6">{action}</div>}
        </div>
    );
}
```

---

## Accesibilidad (a11y)

### Requisitos WCAG 2.1 AA

| Criterio | Implementación |
|----------|----------------|
| **Contraste** | Texto `text-white/70` mínimo sobre fondos glass |
| **Focus visible** | `focus-visible:ring-2 focus-visible:ring-white/20` |
| **Touch target** | Mínimo `h-11` (44px) para elementos interactivos |
| **Keyboard** | Todos los elementos interactivos accesibles con Tab |
| **Screen readers** | `aria-label`, `aria-describedby`, `role` apropiados |

### Patrones de Accesibilidad

```tsx
// Iconos decorativos
<Icon aria-hidden="true" />

// Iconos como único contenido
<button aria-label="Cerrar modal">
    <X aria-hidden="true" />
</button>

// Estados de error en inputs
<input
    aria-invalid={hasError}
    aria-describedby={hasError ? "error-message" : undefined}
/>
<span id="error-message" role="alert">{errorText}</span>

// Loading states
<button disabled aria-busy="true">
    <Loader2 className="animate-spin" aria-hidden="true" />
    <span>Procesando...</span>
</button>

// Modales
<div
    role="dialog"
    aria-modal="true"
    aria-labelledby="modal-title"
>
```

### Focus Trap para Modales

```tsx
// Usar focus-trap-react o implementar manualmente
import { FocusTrap } from "focus-trap-react";

<FocusTrap active={isOpen}>
    <div>{/* Modal content */}</div>
</FocusTrap>
```

---

## Internacionalización (i18n)

### Reglas para Componentes

| Tipo de Texto | Tratamiento |
|---------------|-------------|
| Labels visibles | Siempre usar `t()` |
| Placeholders | Siempre usar `t()` |
| Aria-labels | Siempre usar `t()` |
| Mensajes de error | Siempre usar `t()` |
| Tooltips | Siempre usar `t()` |

### Patrón: Componente con Traducción por Props

```tsx
interface ButtonProps {
    labelKey?: string;        // Key de i18n
    children?: React.ReactNode; // O children directo
}

function ActionButton({ labelKey, children }: ButtonProps) {
    const t = useTranslations("common");

    return (
        <button>
            {labelKey ? t(labelKey) : children}
        </button>
    );
}

// Uso
<ActionButton labelKey="save" />
<ActionButton>Custom Text</ActionButton>
```

### Patrón: Namespace Configurable

```tsx
interface Props {
    namespace?: string;
}

function MyComponent({ namespace = "common" }: Props) {
    const t = useTranslations(namespace);
    // ...
}
```

---

## Tokens de Diseño

### Colores Glass

```tsx
// Fondos
"bg-white/5"              // Glass ligero
"bg-white/10"             // Glass medio
"bg-black/20"             // Glass oscuro (dark mode)
"bg-zinc-900/80"          // Solid alternativo

// Bordes
"border-white/5"          // Muy sutil
"border-white/10"         // Standard
"border-white/20"         // Hover/Focus

// Texto
"text-white"              // Primario
"text-white/90"           // Headings
"text-white/70"           // Body
"text-white/50"           // Secondary
"text-white/40"           // Muted
"text-white/30"           // Placeholder
```

### Espaciado

```tsx
// Padding interno de cards
"p-4"   // sm (16px)
"p-6"   // md (24px) - default
"p-8"   // lg (32px)

// Gap entre elementos
"gap-2" // 8px
"gap-4" // 16px
"gap-6" // 24px
```

### Border Radius

```tsx
"rounded-lg"   // 8px - buttons pequeños
"rounded-xl"   // 12px - inputs, buttons
"rounded-2xl"  // 16px - cards, modales
```

---

## Checklist de Verificación

### Estructura
- [ ] Archivo en ubicación correcta (`ui/glass/` o `[feature]/`)
- [ ] Usa `forwardRef` si es componente primitivo
- [ ] Exporta tipos/interfaces

### Estilo
- [ ] Mobile First implementado
- [ ] Variantes Glass correctas (`bg-white/5`, `backdrop-blur`)
- [ ] Sin colores saturados (solo grises y acentos mínimos)
- [ ] Transiciones suaves (`transition-all duration-200`)

### Accesibilidad
- [ ] Touch target mínimo 44px (`h-11`)
- [ ] Focus visible implementado
- [ ] `aria-*` atributos donde aplica
- [ ] Iconos tienen `aria-hidden="true"` o `aria-label`
- [ ] Contraste suficiente (4.5:1 texto normal, 3:1 texto grande)

### i18n
- [ ] No hay textos hardcodeados
- [ ] Usa `useTranslations()` para textos visibles
- [ ] Labels de accesibilidad también traducidos

---

## Errores Comunes

### Error: "Texto ilegible en modo oscuro"

**Causa:** Usar `text-black` hardcodeado.

**Solución:** Usar variables semánticas: `text-white/70`, `text-foreground`.

### Error: "Glass muy opaco"

**Causa:** Usar `bg-white/50` o más.

**Solución:** Mantener opacidad baja (`/5` a `/10`) y confiar en `backdrop-blur`.

### Error: "Botón no cliceable en móvil"

**Causa:** Altura menor a 44px.

**Solución:** Usar mínimo `h-11` para elementos touch.

### Error: "Focus no visible"

**Causa:** Usar `outline-none` sin alternativa.

**Solución:** Usar `focus-visible:ring-2 focus-visible:ring-white/20`.

---

## Referencias

- [Tailwind Config](../../frontend/tailwind.config.ts)
- [Globals CSS](../../frontend/src/app/globals.css)
- [Componentes Glass existentes](../../frontend/src/components/ui/glass/)
- [Skill add-i18n-keys](../add-i18n-keys/SKILL.md)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

*Última actualización: 2025-02-04*
