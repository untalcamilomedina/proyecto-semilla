---
name: create-design-component
description: Guía para crear componentes UI siguiendo el Design System "Google Glass Minimalist" (Mobile First, B&W).
author: AppNotion Design Team
version: 1.0.0
---

# Skill: Crear Componente de Diseño

Esta skill estandariza la creación de componentes visuales (Atomos/Moleculas) bajo la estética "Tech Minimalist" del proyecto.

## Principios de Diseño

1.  **Mobile First**: Se empieza con layout móvil (`w-full`, `block`) y se adapta a desktop (`md:w-auto`, `md:flex`).
2.  **Glassmorphism Sutil**: Fondos translúcidos, bordes finos, desenfoque (`backdrop-blur`).
3.  **Black & White Puro**: Evitar colores saturados. Usar escala de grises (`zinc-50` a `zinc-950`).
4.  **Tipografía Clara**: Simular Roboto/Montserrat con `font-sans` y pesos claros (`font-medium` para headings).

## Prerrequisitos

- [ ] Tailwind CSS configurado.
- [ ] Ubicación: `frontend/src/components/ui/glass/`.

## Proceso

### Paso 1: Definir Estructura y Props

Identificar qué variantes necesita el componente (ej. `primary`, `secondary`, `outline`).

### Paso 2: Crear Archivo

**Ubicación**: `frontend/src/components/ui/glass/<ComponentName>.tsx`

```tsx
import { cn } from "@/lib/utils";
import React from "react";

interface Props extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "glass" | "solid";
}

export const GlassCard = ({
  className,
  variant = "glass",
  children,
  ...props
}: Props) => {
  return (
    <div
      className={cn(
        // Base Layout (Mobile First)
        "w-full p-4 rounded-xl transition-all duration-300",
        // Typography
        "font-sans text-foreground",
        // Variants
        variant === "glass" && [
          "bg-white/5 dark:bg-black/20", // Translucency
          "backdrop-blur-md", // Glass Effect
          "border border-white/10 dark:border-white/5", // Subtle Border
          "shadow-sm hover:shadow-md", // Minimal Elevation
        ],
        variant === "solid" && "bg-background border border-border",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
};
```

### Paso 3: Estilizar Botones e Inputs

Mantener la consistencia "Tactil":

- **Inputs**: Altura generosa (44px+), placeholder suave.
- **Botones**: Sin gradientes agresivos, usar hover en opacidad.

## Checklist de Verificación de Estilo

- [ ] **Mobile First**: ¿Se ve bien en 320px de ancho?
- [ ] **Contraste**: ¿El texto es legible (`text-foreground`) sobre el fondo glass?
- [ ] **Borde**: ¿Tiene ese borde sutil (`border-white/10`) que define el cristal?
- [ ] **Sin Color**: ¿He evitado azules/rojos/verdes a menos que sea un error/éxito crítico?

## Errores Comunes

### Error: "Texto ilegible en modo oscuro"

**Causa:** Usar `text-black` hardcodeado.
**Solución:** Usar siempre variables semánticas: `text-foreground` o `text-primary`.

### Error: "Glass muy opaco"

**Causa:** Usar `bg-white/50` o más.
**Solución:** Mantener la opacidad baja (`/5` a `/10`) y confiar en el `backdrop-blur`.

## Referencias

- [Tailwind Config](../../../../frontend/tailwind.config.ts)
- [Globals CSS](../../../../frontend/src/app/globals.css)
