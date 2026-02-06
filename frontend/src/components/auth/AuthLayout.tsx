"use client";

import React from "react";
import { BlockFlowLogo } from "@/components/ui/logo";
import { GlassCard } from "@/components/ui/glass/GlassCard";
import { cn } from "@/lib/utils";

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  description: string;
}

/**
 * AuthLayout
 * Provides a consistent glassmorphic background and container for login/signup pages.
 * 
 * @vibe Elite/Enterprise - Consistent with onboarding aesthetic but without stepper.
 */
export function AuthLayout({ children, title, description }: AuthLayoutProps) {
  return (
    <main className="min-h-screen w-full flex items-center justify-center bg-zinc-950 p-4 relative overflow-hidden">
      {/* Background Ambience - Same as Onboarding for visual unity */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-neon/5 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-[-10%] left-[-5%] w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-3xl animate-pulse" />
      </div>

      <section className="w-full max-w-md z-10 space-y-8">
        <GlassCard className="p-8 md:p-10 w-full flex flex-col relative overflow-hidden border-white/10 bg-black/40" as="article">
          {/* Decorative Glow inside Card */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2/3 h-1 bg-gradient-to-r from-transparent via-neon/50 to-transparent opacity-50" />
          
          <div className="space-y-6 mb-8 text-center flex flex-col items-center">
            <BlockFlowLogo className="h-16 w-16" color="white" />
            <span className="text-2xl font-bold text-white tracking-tight mt-2">BlockFlow Platform</span>
            
            <div className="space-y-2">
                <h1 className="text-3xl font-bold bg-gradient-to-b from-white to-white/60 bg-clip-text text-transparent">
                  {title}
                </h1>
                <p className="text-white/50 text-sm">{description}</p>
            </div>
          </div>

          <div className="flex-1">
            {children}
          </div>
        </GlassCard>
      </section>
    </main>
  );
}
