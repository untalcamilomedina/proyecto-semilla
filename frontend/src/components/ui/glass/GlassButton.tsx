import { cn } from "@/lib/utils";
import React from "react";

interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "danger";
}

export function GlassButton({ children, className, variant = "primary", ...props }: GlassButtonProps) {
  return (
    <button
      className={cn(
        "px-4 py-2 rounded-xl backdrop-blur-md transition-all duration-300 font-medium",
        "hover:scale-[1.01] active:scale-95",
        
        // Primary (Neon Green)
        variant === "primary" && 
          "bg-primary/20 text-emerald-100 border border-primary/50 hover:bg-primary/30 shadow-neon",
        
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
