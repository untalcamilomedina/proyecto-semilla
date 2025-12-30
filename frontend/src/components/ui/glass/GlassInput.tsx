import * as React from "react"
import { cn } from "@/lib/utils"

export interface GlassInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

/**
 * GlassInput Component
 * Renders an input field with glassmorphism styling and neon focus effects.
 * 
 * @param {GlassInputProps} props - Standard HTML input attributes.
 * @param {string} props.className - Additional CSS classes.
 * @param {string} props.type - Input type (text, password, etc).
 * @param {React.Ref<HTMLInputElement>} ref - Forwarded ref.
 * @returns {JSX.Element} The rendered input component.
 */
export const GlassInput = React.forwardRef<HTMLInputElement, GlassInputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neon focus-visible:border-neon/50 disabled:cursor-not-allowed disabled:opacity-50 text-white transition-all duration-300",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
GlassInput.displayName = "GlassInput"
