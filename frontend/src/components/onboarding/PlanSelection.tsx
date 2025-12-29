"use client";

import React, { useState } from "react";
import { GlassCard } from "@/components/ui/glass/GlassCard";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { useOnboardingStore } from "@/stores/onboarding";
import { useRouter } from "next/navigation";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

const PLANS = [
  {
    id: "starter",
    name: "Starter",
    price: { monthly: 0, yearly: 0 },
    features: ["Up to 5 members", "Basic Support", "1GB Storage"],
  },
  {
    id: "pro",
    name: "Pro",
    price: { monthly: 29, yearly: 290 },
    features: ["Unlimited members", "Priority Support", "100GB Storage", "Analytics"],
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: { monthly: 99, yearly: 990 },
    features: ["Custom SLA", "Dedicated Account Manager", "Unlimited Storage", "SSO"],
  },
];

export default function PlanSelection() {
  const { planId, billingPeriod, setPlan, nextStep } = useOnboardingStore();
  const router = useRouter();
  const [period, setPeriod] = useState<'monthly' | 'yearly'>(billingPeriod);

  const handleSelect = (id: string) => {
    setPlan(id, period);
  };

  const handleContinue = () => {
    if (planId) {
      nextStep();
      router.push("/onboarding/payment");
    }
  };

  return (
    <div className="space-y-8 animate-in slide-in-from-right-8 duration-500">
      {/* Toggle */}
      <div className="flex justify-center">
        <div className="bg-white/5 p-1 rounded-xl flex">
          <button
            onClick={() => setPeriod('monthly')}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-all",
              period === 'monthly' ? "bg-white/10 text-white shadow-sm" : "text-white/50 hover:text-white"
            )}
          >
            Monthly
          </button>
          <button
            onClick={() => setPeriod('yearly')}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-all",
              period === 'yearly' ? "bg-white/10 text-white shadow-sm" : "text-white/50 hover:text-white"
            )}
          >
            Yearly <span className="text-neon text-xs ml-1">-20%</span>
          </button>
        </div>
      </div>

      {/* Plans Grid */}
      <div className="grid md:grid-cols-3 gap-4">
        {PLANS.map((plan) => {
          const isSelected = planId === plan.id;
          return (
            <GlassCard
              key={plan.id}
              variant={isSelected ? "neon" : "default"}
              className={cn(
                "p-6 cursor-pointer relative transition-all hover:scale-[1.02]",
                isSelected ? "border-neon/50 bg-neon/5" : "hover:border-white/20"
              )}
              onClick={() => handleSelect(plan.id)}
            >
              {isSelected && (
                <div className="absolute top-4 right-4 text-neon">
                  <Check className="w-5 h-5" />
                </div>
              )}
              <h3 className="text-lg font-bold text-white mb-2">{plan.name}</h3>
              <div className="text-3xl font-bold text-white mb-4">
                ${period === 'monthly' ? plan.price.monthly : Math.round(plan.price.yearly / 12)}
                <span className="text-sm text-white/40 font-normal">/mo</span>
              </div>
              <ul className="space-y-2 mb-6">
                {plan.features.map((f, i) => (
                  <li key={i} className="text-sm text-white/70 flex items-center gap-2">
                    <Check className="w-3 h-3 text-neon" /> {f}
                  </li>
                ))}
              </ul>
            </GlassCard>
          );
        })}
      </div>

      <GlassButton 
        onClick={handleContinue} 
        disabled={!planId} 
        className="w-full disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Continue
      </GlassButton>
    </div>
  );
}
