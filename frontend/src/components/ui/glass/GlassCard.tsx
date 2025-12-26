import { cn } from "@/lib/utils";
import React from "react";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: "default" | "neon";
}

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
