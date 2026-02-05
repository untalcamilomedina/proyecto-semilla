---
name: create-micro-interaction
description: Guía para crear micro-interacciones, animaciones y skeleton loaders estilo Notion/Google.
author: AppNotion Design Team
version: 1.0.0
---

# Skill: Crear Micro-Interacciones

Esta skill estandariza la creación de micro-interacciones que dan el "polish" profesional característico de Notion y Google. Incluye animaciones de hover, transiciones, skeleton loaders, y feedback visual.

## Principios de Micro-Interacciones

| Principio | Descripción | Ejemplo |
|-----------|-------------|---------|
| **Sutileza** | Animaciones apenas perceptibles | Hover: `opacity-80` → `opacity-100` |
| **Rapidez** | Transiciones cortas (150-300ms) | `duration-200` es ideal |
| **Propósito** | Cada animación comunica algo | Loading = skeleton, success = check |
| **Consistencia** | Mismo timing en toda la app | Siempre `ease-out` para entradas |

## Prerrequisitos

- [ ] Tailwind CSS configurado.
- [ ] Plugin `tw-animate-css` instalado (ya presente en el proyecto).

## Cuándo Usar

- Al crear componentes interactivos (botones, links, cards).
- Para estados de carga (skeleton loaders).
- En transiciones de página/modal.
- Para feedback de acciones (success, error).

---

## Catálogo de Micro-Interacciones

### 1. Hover States (Estilo Notion)

#### Link con Underline Animado

```tsx
export function NotionLink({ href, children }: { href: string; children: React.ReactNode }) {
    return (
        <a
            href={href}
            className="relative text-foreground/80 hover:text-foreground transition-colors duration-200 group"
        >
            {children}
            {/* Underline que aparece en hover */}
            <span className="absolute left-0 bottom-0 w-0 h-[1px] bg-foreground/50 group-hover:w-full transition-all duration-300" />
        </a>
    );
}
```

#### Card con Hover Sutil

```tsx
export function HoverCard({ children }: { children: React.ReactNode }) {
    return (
        <div
            className={cn(
                "p-4 rounded-lg border border-transparent",
                "transition-all duration-200",
                // Hover state estilo Notion
                "hover:bg-muted/50 hover:border-border/50",
                // Cursor
                "cursor-pointer"
            )}
        >
            {children}
        </div>
    );
}
```

#### Button con Scale Sutil

```tsx
export function PressableButton({ children, ...props }: ButtonProps) {
    return (
        <button
            className={cn(
                "transition-all duration-150",
                // Hover
                "hover:bg-muted",
                // Active (press)
                "active:scale-[0.98] active:opacity-90"
            )}
            {...props}
        >
            {children}
        </button>
    );
}
```

### 2. Skeleton Loaders

#### Skeleton Base Component

```tsx
import { cn } from "@/lib/utils";

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: "text" | "circular" | "rectangular";
}

export function Skeleton({ className, variant = "text", ...props }: SkeletonProps) {
    return (
        <div
            className={cn(
                // Base animation
                "animate-pulse bg-muted",
                // Variants
                variant === "text" && "h-4 rounded",
                variant === "circular" && "rounded-full",
                variant === "rectangular" && "rounded-lg",
                className
            )}
            {...props}
        />
    );
}
```

#### Skeleton Card (Ejemplo Notion)

```tsx
export function SkeletonCard() {
    return (
        <div className="p-4 space-y-4 border border-border rounded-lg">
            {/* Avatar + Title */}
            <div className="flex items-center gap-3">
                <Skeleton variant="circular" className="h-10 w-10" />
                <div className="space-y-2 flex-1">
                    <Skeleton className="h-4 w-1/3" />
                    <Skeleton className="h-3 w-1/4" />
                </div>
            </div>
            {/* Content lines */}
            <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6" />
                <Skeleton className="h-4 w-4/6" />
            </div>
        </div>
    );
}
```

#### Skeleton Table Row

```tsx
export function SkeletonTableRow() {
    return (
        <tr className="border-b border-border">
            <td className="p-4">
                <div className="flex items-center gap-3">
                    <Skeleton variant="circular" className="h-8 w-8" />
                    <Skeleton className="h-4 w-32" />
                </div>
            </td>
            <td className="p-4">
                <Skeleton className="h-4 w-24" />
            </td>
            <td className="p-4">
                <Skeleton className="h-6 w-16 rounded-full" />
            </td>
            <td className="p-4">
                <Skeleton className="h-4 w-20" />
            </td>
        </tr>
    );
}
```

### 3. Transiciones de Entrada/Salida

#### Page Transition (Notion-style)

```tsx
export function PageTransition({ children }: { children: React.ReactNode }) {
    return (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-300">
            {children}
        </div>
    );
}
```

#### Modal Transition

```tsx
export function ModalTransition({ open, children }: { open: boolean; children: React.ReactNode }) {
    if (!open) return null;

    return (
        <>
            {/* Backdrop */}
            <div className="fixed inset-0 bg-black/50 animate-in fade-in duration-200" />
            {/* Modal */}
            <div className="fixed inset-0 flex items-center justify-center p-4">
                <div className="animate-in fade-in zoom-in-95 duration-200">
                    {children}
                </div>
            </div>
        </>
    );
}
```

#### List Item Stagger (Animación escalonada)

```tsx
interface StaggeredListProps {
    items: React.ReactNode[];
    staggerDelay?: number; // ms between each item
}

export function StaggeredList({ items, staggerDelay = 50 }: StaggeredListProps) {
    return (
        <div className="space-y-2">
            {items.map((item, index) => (
                <div
                    key={index}
                    className="animate-in fade-in slide-in-from-left-2"
                    style={{ animationDelay: `${index * staggerDelay}ms` }}
                >
                    {item}
                </div>
            ))}
        </div>
    );
}
```

### 4. Loading States

#### Spinner Minimalista

```tsx
export function Spinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
    const sizeClasses = {
        sm: "h-4 w-4 border-2",
        md: "h-6 w-6 border-2",
        lg: "h-8 w-8 border-3",
    };

    return (
        <div
            className={cn(
                "rounded-full border-muted-foreground/30 border-t-foreground animate-spin",
                sizeClasses[size]
            )}
        />
    );
}
```

#### Dots Loading (Google-style)

```tsx
export function DotsLoading() {
    return (
        <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
                <div
                    key={i}
                    className="h-2 w-2 rounded-full bg-foreground/60 animate-bounce"
                    style={{ animationDelay: `${i * 150}ms` }}
                />
            ))}
        </div>
    );
}
```

#### Progress Bar

```tsx
interface ProgressBarProps {
    value: number; // 0-100
    indeterminate?: boolean;
}

export function ProgressBar({ value, indeterminate }: ProgressBarProps) {
    return (
        <div className="h-1 w-full bg-muted rounded-full overflow-hidden">
            <div
                className={cn(
                    "h-full bg-foreground rounded-full transition-all duration-300",
                    indeterminate && "animate-progress-indeterminate"
                )}
                style={indeterminate ? undefined : { width: `${value}%` }}
            />
        </div>
    );
}
```

Agregar a `globals.css`:
```css
@keyframes progress-indeterminate {
    0% { transform: translateX(-100%); width: 30%; }
    50% { transform: translateX(100%); width: 30%; }
    100% { transform: translateX(300%); width: 30%; }
}

.animate-progress-indeterminate {
    animation: progress-indeterminate 1.5s ease-in-out infinite;
}
```

### 5. Feedback Visual

#### Success Check Animation

```tsx
import { Check } from "lucide-react";

export function SuccessCheck() {
    return (
        <div className="flex items-center justify-center h-12 w-12 rounded-full bg-green-500/10 animate-in zoom-in duration-200">
            <Check className="h-6 w-6 text-green-500 animate-in fade-in duration-300 delay-100" />
        </div>
    );
}
```

#### Toast Notification

```tsx
interface ToastProps {
    message: string;
    type?: "success" | "error" | "info";
    onClose: () => void;
}

export function Toast({ message, type = "info", onClose }: ToastProps) {
    const icons = {
        success: <Check className="h-4 w-4 text-green-500" />,
        error: <X className="h-4 w-4 text-red-500" />,
        info: <Info className="h-4 w-4 text-blue-500" />,
    };

    return (
        <div
            className={cn(
                "fixed bottom-4 right-4 z-50",
                "flex items-center gap-3 px-4 py-3",
                "bg-card border border-border rounded-lg shadow-lg",
                "animate-in slide-in-from-bottom-4 fade-in duration-300"
            )}
        >
            {icons[type]}
            <span className="text-sm">{message}</span>
            <button
                onClick={onClose}
                className="ml-2 text-muted-foreground hover:text-foreground transition-colors"
            >
                <X className="h-4 w-4" />
            </button>
        </div>
    );
}
```

### 6. Ripple Effect (Google Material)

```tsx
"use client";

import { useState, useCallback } from "react";

interface RippleProps {
    color?: string;
}

export function useRipple(color: string = "rgba(255,255,255,0.3)") {
    const [ripples, setRipples] = useState<{ x: number; y: number; id: number }[]>([]);

    const addRipple = useCallback((event: React.MouseEvent<HTMLElement>) => {
        const rect = event.currentTarget.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const id = Date.now();

        setRipples((prev) => [...prev, { x, y, id }]);
        setTimeout(() => {
            setRipples((prev) => prev.filter((r) => r.id !== id));
        }, 600);
    }, []);

    const Ripples = () => (
        <>
            {ripples.map((ripple) => (
                <span
                    key={ripple.id}
                    className="absolute rounded-full animate-ripple pointer-events-none"
                    style={{
                        left: ripple.x,
                        top: ripple.y,
                        backgroundColor: color,
                        transform: "translate(-50%, -50%)",
                    }}
                />
            ))}
        </>
    );

    return { addRipple, Ripples };
}
```

Agregar a `globals.css`:
```css
@keyframes ripple {
    from {
        width: 0;
        height: 0;
        opacity: 0.5;
    }
    to {
        width: 200px;
        height: 200px;
        opacity: 0;
    }
}

.animate-ripple {
    animation: ripple 0.6s linear;
}
```

Uso:
```tsx
function RippleButton({ children }: { children: React.ReactNode }) {
    const { addRipple, Ripples } = useRipple();

    return (
        <button
            onClick={addRipple}
            className="relative overflow-hidden px-4 py-2 bg-primary text-primary-foreground rounded-lg"
        >
            <Ripples />
            {children}
        </button>
    );
}
```

---

## Tokens de Animación

### Duración

| Token | Valor | Uso |
|-------|-------|-----|
| `duration-150` | 150ms | Micro-interacciones (hover, active) |
| `duration-200` | 200ms | Transiciones estándar |
| `duration-300` | 300ms | Entradas/salidas de componentes |
| `duration-500` | 500ms | Transiciones de página |

### Easing

| Token | Curva | Uso |
|-------|-------|-----|
| `ease-out` | Desacelera al final | Entradas (recomendado) |
| `ease-in` | Acelera al inicio | Salidas |
| `ease-in-out` | Suave en ambos | Transiciones largas |

### Delay (para stagger)

```tsx
// Patrón de delay escalonado
style={{ animationDelay: `${index * 50}ms` }}
```

---

## Checklist de Verificación

### Animaciones
- [ ] Duración ≤ 300ms para interacciones directas
- [ ] Usa `ease-out` para entradas
- [ ] No hay "flash" o parpadeo
- [ ] Funciona bien a 60fps

### Skeleton Loaders
- [ ] Dimensiones coinciden con contenido real
- [ ] `animate-pulse` aplicado
- [ ] Color usa `bg-muted`

### Accesibilidad
- [ ] `prefers-reduced-motion` respetado (ver siguiente sección)
- [ ] Animaciones no causan mareo
- [ ] No hay contenido que parpadee >3 veces/segundo

### Respeto a `prefers-reduced-motion`

```css
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

---

## Errores Comunes

### Error: Animación se siente "lenta"

**Causa:** Duración muy larga.

**Solución:** Usar `duration-200` máximo para hover states.

### Error: Skeleton "salta" cuando carga contenido

**Causa:** Dimensiones del skeleton no coinciden.

**Solución:** Medir contenido real y usar mismas dimensiones.

### Error: Animación no se reproduce al re-render

**Causa:** Falta key única en elemento animado.

**Solución:** Agregar `key={uniqueId}` para forzar re-mount.

---

## Referencias

- [Tailwind Animate](https://github.com/jamiebuilds/tailwindcss-animate)
- [Framer Motion (alternativa)](https://www.framer.com/motion/)
- [Material Design Motion](https://material.io/design/motion/)

---

*Última actualización: 2025-02-04*
