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
 * @param {React.ElementType} [props.as='div'] - Elemento HTML a renderizar (e.g. 'article', 'section').
 */
export const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ children, className, variant = "default", as: Component = "div", ...props }, ref) => {
    return (
      <Component
        ref={ref}
        className={cn(
          "rounded-2xl backdrop-blur-xl border border-white/10 transition-all duration-300",
          "bg-white/5",
          variant === "neon" && "shadow-neon border-primary/20",
          variant === "default" && "shadow-glass",
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
