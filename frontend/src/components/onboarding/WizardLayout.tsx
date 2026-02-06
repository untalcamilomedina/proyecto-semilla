"use client";

import React from "react";
import { GlassCard } from "@/components/ui/glass/GlassCard";
import { useOnboardingStore } from "@/stores/onboarding";
import { cn } from "@/lib/utils";
import { Check } from "lucide-react";

interface WizardLayoutProps {
  children: React.ReactNode;
  title: string;
  description: string;
}

const STEPS = [
  { number: 1, label: "Profile" },
  { number: 2, label: "Organization" },
  { number: 3, label: "Billing" },
  { number: 4, label: "Review" },
];

/**
 * WizardLayout Component
 * Wraps onboarding steps with a consistent glassmorphic container and progress stepper.
 * Uses semantic tokens for full light/dark theme support.
 */
export function WizardLayout({ children, title, description }: WizardLayoutProps) {
  const store = useOnboardingStore();
  const step = store.step;

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-background p-4 relative overflow-hidden">
      {/* Background Ambience (dark mode only) */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none hidden dark:block">
        <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-neon-bg rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-[-10%] left-[-5%] w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-3xl animate-pulse" />
      </div>

      {/* Language Selector */}
      <div className="absolute top-6 right-6 z-50">
         <GlassCard className="p-1 flex gap-1 rounded-lg bg-glass-overlay backdrop-blur-md border-glass-border">
            <button
              onClick={() => store.setLanguage('es')}
              className={cn(
                "px-3 py-1.5 rounded-md text-xs font-medium transition-all",
                store.language === 'es' ? "bg-neon text-primary-foreground shadow-lg shadow-neon/20" : "text-text-secondary hover:text-foreground"
              )}
            >
              ES
            </button>
            <button
              onClick={() => store.setLanguage('en')}
              className={cn(
                "px-3 py-1.5 rounded-md text-xs font-medium transition-all",
                store.language === 'en' ? "bg-neon text-primary-foreground shadow-lg shadow-neon/20" : "text-text-secondary hover:text-foreground"
              )}
            >
              EN
            </button>
         </GlassCard>
      </div>

      <div className="w-full max-w-4xl z-10 space-y-8">
        {/* Stepper */}
        <div className="flex justify-between items-center px-4 relative">
          <div className="absolute left-0 top-[15px] w-full h-[2px] bg-glass-border-subtle -z-10" />
          <div
            className="absolute left-0 top-[15px] h-[2px] bg-neon/50 -z-10 transition-all duration-500"
            style={{ width: `${((step - 1) / (STEPS.length - 1)) * 100}%` }}
          />

          {STEPS.map((s) => {
            const isActive = s.number === step;
            const isCompleted = s.number < step;

            return (
              <div key={s.number} className="flex flex-col items-center gap-2">
                <div
                  className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all duration-300",
                    isCompleted
                      ? "bg-neon border-neon text-primary-foreground shadow-neon"
                      : isActive
                      ? "bg-surface-raised border-neon text-neon-text shadow-neon scale-110"
                      : "bg-surface-raised border-glass-border text-text-quaternary"
                  )}
                >
                  {isCompleted ? <Check className="w-4 h-4" /> : s.number}
                </div>
                <span
                  className={cn(
                    "text-xs font-medium transition-colors duration-300",
                    isActive || isCompleted ? "text-foreground" : "text-text-quaternary"
                  )}
                >
                  {s.label}
                </span>
              </div>
            );
          })}
        </div>

        {/* Content Card */}
        <GlassCard className="p-8 md:p-12 w-full mx-auto max-w-2xl min-h-[500px] flex flex-col relative overflow-hidden">
          {/* Decorative Glow inside Card (dark only) */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2/3 h-1 bg-gradient-to-r from-transparent via-neon/50 to-transparent opacity-50 hidden dark:block" />

          <div className="space-y-2 mb-8 text-center">
            <h1 className="text-3xl font-bold text-gradient-heading">
              {title}
            </h1>
            <p className="text-text-secondary">{description}</p>
          </div>

          <div className="flex-1">
            {children}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
