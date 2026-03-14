import { cn } from "@/lib/utils";
import React from "react";

/**
 * Props for the GlassCard component.
 * @extends React.HTMLAttributes<HTMLDivElement>
 */
export interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * The visual variant of the card.
   * - \`default\`: Standard glassmorphism container.
   * - \`highlight\`: Uses the primary color for a subtle glow border.
   * @default "default"
   */
  variant?: "default" | "highlight";
  
  /**
   * The HTML element to render the card as.
   * @default "div"
   */
  as?: React.ElementType;
}

/**
 * 🧊 GlassCard
 * 
 * Core container component implementing the Glass Minimalist design system.
 * Built with backdrop-blur, subtle borders, and semantic tokens to support
 * seamless light/dark mode and tenant theming.
 * 
 * @example
 * \`\`\`tsx
 * <GlassCard variant="highlight" className="p-6">
 *   <h3>Card Content</h3>
 * </GlassCard>
 * \`\`\`
 */
export const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ children, className, variant = "default", as: Component = "div", ...props }, ref) => {
    return (
      <Component
        ref={ref}
        className={cn(
          // Base properties
          "rounded-2xl backdrop-blur-md border transition-all duration-300",
          "bg-glass-bg",
          
          // Variants
          variant === "default" && "border-glass-border shadow-sm",
          variant === "highlight" && "border-primary/50 shadow-md shadow-primary/10",
          
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
