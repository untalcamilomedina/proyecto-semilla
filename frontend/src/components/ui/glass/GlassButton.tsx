import { cn } from "@/lib/utils";
import React from "react";

/**
 * Props for the GlassButton component.
 * @extends React.ButtonHTMLAttributes<HTMLButtonElement>
 */
export interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** 
   * The visual variant of the button. 
   * - \`primary\`: Uses the primary branding color with a solid/glass hybrid look.
   * - \`secondary\`: Fully transparent glass look with border.
   * - \`danger\`: Uses the semantic error palette.
   * @default "primary"
   */
  variant?: "primary" | "secondary" | "danger";
  
  /**
   * The size of the button. Touch targets scale accordingly.
   * @default "md"
   */
  size?: "sm" | "md" | "lg";
  
  /**
   * Shows a loading spinner and disables interactions.
   * @default false
   */
  isLoading?: boolean;
}

/**
 * 🧊 GlassButton
 * 
 * An interactive button component implementing the Glass Minimalist design system.
 * Built for Dark/Light mode, mobile-first touch targets, and full accessibility.
 * 
 * @example
 * \`\`\`tsx
 * <GlassButton variant="primary" size="lg" onClick={handleClick}>
 *   Save Changes
 * </GlassButton>
 * \`\`\`
 */
export const GlassButton = React.forwardRef<HTMLButtonElement, GlassButtonProps>(
  ({ children, className, variant = "primary", size = "md", isLoading, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          // Base & animations
          "inline-flex items-center justify-center rounded-xl backdrop-blur-md transition-all duration-300 font-medium",
          "hover:scale-[1.01] active:scale-[0.98]",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50",
          "disabled:opacity-50 disabled:cursor-not-allowed",

          // Sizes (mobile-first touch targets: min 44px for interaction generally)
          size === "sm" && "h-9 px-4 text-sm",
          size === "md" && "h-11 px-6 text-sm",
          size === "lg" && "h-12 px-8 text-base",

          // Variants using EXCLUSIVELY semantic tokens from the JSON theme
          variant === "primary" &&
            "bg-primary/90 text-primary-foreground border border-primary/20 hover:bg-primary shadow-lg shadow-primary/20",

          variant === "secondary" &&
            "bg-glass-bg text-foreground border border-glass-border hover:bg-muted",

          variant === "danger" &&
            "bg-error-bg text-error-text border border-error-border hover:bg-error-bg/80",

          className
        )}
        {...props}
      >
        {isLoading ? (
          <span 
            className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
            aria-hidden="true" 
          />
        ) : null}
        {children}
      </button>
    );
  }
);

GlassButton.displayName = "GlassButton";
