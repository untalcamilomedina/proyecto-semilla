import { cn } from "@/lib/utils";
import React from "react";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: "default" | "neon";
}

/**
 * GlassCard Component
 * Renders a container with glassmorphism effects (backdrop blur, border).
 * 
 * @param {ReactNode} children - Card content.
 * @param {string} className - Additional classes.
 * @param {"default" | "neon"} variant - Visual style variant.
 * @param {HTMLAttributes} props - Standard HTML div attributes.
 */
export function GlassCard({ children, className, variant = "default", ...props }: GlassCardProps) {
  return (
    <div
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
    </div>
  );
}
