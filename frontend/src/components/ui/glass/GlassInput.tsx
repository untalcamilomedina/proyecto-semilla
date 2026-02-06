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
        {label && <label htmlFor={inputId} className="text-xs font-medium text-white/50 ml-1">{label}</label>}
        <input
          id={inputId}
          type={type}
          className={cn(
            "flex h-11 w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-white placeholder:text-white/50 transition-all duration-300",
            "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neon focus-visible:border-neon/50",
            "disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-red-500/50 focus-visible:ring-red-500 focus-visible:border-red-500/50",
            className
          )}
          ref={ref}
          {...props}
        />
        {error && <p className="text-[10px] text-red-400 ml-1 font-medium anonymous-fade-in">{error}</p>}
      </div>
    )
  }
)
GlassInput.displayName = "GlassInput"
