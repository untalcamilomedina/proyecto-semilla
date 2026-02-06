"use client";

import React from "react";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { useOnboardingStore } from "@/stores/onboarding";
import { useRouter } from "@/lib/navigation";
import { CreditCard, Lock } from "lucide-react";

export default function PaymentSetup() {
  const { nextStep } = useOnboardingStore();
  const router = useRouter();

  const handleContinue = (e: React.FormEvent) => {
    e.preventDefault();
    nextStep();
    router.push("/onboarding/review");
  };

  return (
    <form onSubmit={handleContinue} className="space-y-6 animate-in slide-in-from-right-8 duration-500">
      <div className="bg-glass-bg p-4 rounded-xl border border-glass-border space-y-4">
        <div className="flex items-center justify-between text-text-subtle text-sm mb-2">
          <div className="flex items-center gap-2">
            <CreditCard className="w-4 h-4" />
            Credit Card
          </div>
          <div className="flex items-center gap-1 text-xs">
             <Lock className="w-3 h-3" /> Secure
          </div>
        </div>

        <GlassInput placeholder="Card number" className="font-mono" />

        <div className="grid grid-cols-2 gap-4">
          <GlassInput placeholder="MM / YY" className="font-mono text-center" />
          <GlassInput placeholder="CVC" className="font-mono text-center" />
        </div>

        <GlassInput placeholder="Cardholder name" />
      </div>

      <div className="text-center text-xs text-text-tertiary">
        This is a demo payment form. No actual charge will be made.
      </div>

      <GlassButton type="submit" className="w-full">
        Continue to Review
      </GlassButton>
    </form>
  );
}
