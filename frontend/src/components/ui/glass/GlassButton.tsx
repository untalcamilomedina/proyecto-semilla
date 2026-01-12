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
          "px-4 py-2 rounded-xl backdrop-blur-md transition-all duration-300 font-medium",
          "hover:scale-[1.01] active:scale-95",
          
          // Primary (Neon Green)
          variant === "primary" && 
            "bg-neon/20 text-neon border border-neon/50 hover:bg-neon/30 shadow-[0_0_15px_rgba(13,242,13,0.3)]",
          
          // Secondary
          variant === "secondary" && 
            "bg-white/5 text-zinc-100 border border-white/10 hover:bg-white/10",
            
          // Danger
          variant === "danger" && 
            "bg-red-500/20 text-red-100 border border-red-500/30 hover:bg-red-500/30",

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
