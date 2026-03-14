import * as React from "react"
import { cn } from "@/lib/utils"

/**
 * Props for the GlassInput component.
 * @extends React.InputHTMLAttributes<HTMLInputElement>
 */
export interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /**
   * Optional accessible label displayed above the input.
   */
  label?: string;
  
  /**
   * Optional error message. If provided, the input border turns red and the message is displayed below.
   */
  error?: string;
}

/**
 * 🧊 GlassInput
 * 
 * Form input field implementing the Glass Minimalist design system.
 * Uses semantic tokens for focus rings (primary) and error states.
 * 
 * @example
 * \`\`\`tsx
 * <GlassInput 
 *   label="Email Address" 
 *   type="email" 
 *   placeholder="name@company.com" 
 * />
 * \`\`\`
 */
export const GlassInput = React.forwardRef<HTMLInputElement, GlassInputProps>(
  ({ className, type, label, error, id, ...props }, ref) => {
    const generatedId = React.useId();
    const inputId = id || generatedId;

    return (
      <div className="space-y-2 w-full">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-foreground ml-1">
            {label}
          </label>
        )}
        <input
          id={inputId}
          type={type}
          className={cn(
            // Base styles
            "flex h-11 w-full rounded-xl border border-glass-border bg-glass-bg px-4 py-2",
            "text-sm text-foreground transition-all duration-300",
            
            // Placeholder
            "placeholder:text-muted-foreground",
            
            // Focus state (Primary brand color)
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:border-primary/50",
            
            // Disabled state
            "disabled:cursor-not-allowed disabled:opacity-50",
            
            // Error state
            error && "border-error-border focus-visible:ring-error-text focus-visible:border-error-border",
            
            className
          )}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="text-xs text-error-text ml-1 font-medium animate-in fade-in py-1">
            {error}
          </p>
        )}
      </div>
    )
  }
)
GlassInput.displayName = "GlassInput"
