import * as React from "react"
import { cn } from "@/lib/utils"

export interface GlassInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    id?: string;
}

/**
 * GlassInput
 * Campo de entrada de datos con estilo glassmorphism y enfoque neón.
 *
 * @vibe Elite - High-end form elements with subtle transparency.
 * @param {string} [props.label] - Etiqueta opcional.
 * @param {string} [props.error] - Mensaje de error opcional.
 */
export const GlassInput = React.forwardRef<HTMLInputElement, GlassInputProps>(
  ({ className, type, label, error, id, ...props }, ref) => {
    const generatedId = React.useId();
    const inputId = id || generatedId;

    return (
      <div className="space-y-1.5 w-full">
        {label && <label htmlFor={inputId} className="text-xs font-medium text-text-secondary ml-1">{label}</label>}
        <input
          id={inputId}
          type={type}
          className={cn(
            "flex h-11 w-full rounded-xl border border-glass-border bg-glass-bg px-4 py-2 text-sm text-foreground placeholder:text-text-secondary transition-all duration-300",
            "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neon focus-visible:border-neon-border",
            "disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-error-border focus-visible:ring-error-text focus-visible:border-error-border",
            className
          )}
          ref={ref}
          {...props}
        />
        {error && <p className="text-[10px] text-error-text ml-1 font-medium anonymous-fade-in">{error}</p>}
      </div>
    )
  }
)
GlassInput.displayName = "GlassInput"
