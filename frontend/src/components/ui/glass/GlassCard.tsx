import { cn } from "@/lib/utils";
import React from "react";

/**
 * GlassCardProps
 * @extends React.HTMLAttributes<HTMLDivElement>
 */
export interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: "default" | "neon";
  as?: React.ElementType;
}

/**
 * GlassCard
 * Contenedor principal con efecto de vidrio esmerilado y borde radiante.
 *
 * @vibe Elite - Core container for premium apps.
 * @param {React.ReactNode} props.children - Contenido embebido.
 * @param {string} [props.variant='default'] - 'default' | 'neon'.
 * @param {React.ElementType} [props.as='div'] - Elemento HTML a renderizar.
 */
export const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ children, className, variant = "default", as: Component = "div", ...props }, ref) => {
    return (
      <Component
        ref={ref}
        className={cn(
          "rounded-2xl backdrop-blur-xl border border-glass-border transition-all duration-300",
          "bg-glass-bg",
          variant === "neon" && "shadow-neon border-neon-border",
          className
        )}
        {...props}
      >
        {children}
      </Component>
    );
  }
);

GlassCard.displayName = "GlassCard";
