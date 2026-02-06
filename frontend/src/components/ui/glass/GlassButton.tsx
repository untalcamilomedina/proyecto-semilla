import { cn } from "@/lib/utils";
import React from "react";

/**
 * GlassButtonProps
 * @extends React.ButtonHTMLAttributes<HTMLButtonElement>
 */
export interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "danger";
}

/**
 * GlassButton
 * Componente de acción principal con efecto de vidrio esmerilado y acentos neón.
 *
 * @vibe Elite - Premium interactive elements with glow and blur.
 * @param {React.ReactNode} props.children - Contenido del botón.
 * @param {string} [props.variant='primary'] - 'primary' | 'secondary' | 'danger'.
 */
export const GlassButton = React.forwardRef<HTMLButtonElement, GlassButtonProps>(
  ({ children, className, variant = "primary", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center px-4 py-2 rounded-xl backdrop-blur-md transition-all duration-300 font-medium",
          "hover:scale-[1.01] active:scale-95",

          variant === "primary" &&
            "bg-neon-bg-strong text-foreground font-bold border border-neon-border hover:bg-neon/30 shadow-neon",

          variant === "secondary" &&
            "bg-glass-bg text-foreground border border-glass-border hover:bg-glass-bg-hover",

          variant === "danger" &&
            "bg-error-bg text-error-text border border-error-border hover:bg-error-bg/80",

          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);

GlassButton.displayName = "GlassButton";
