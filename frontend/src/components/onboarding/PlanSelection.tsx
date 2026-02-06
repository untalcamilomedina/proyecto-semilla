"use client";

import React, { useState } from "react";
import { GlassCard } from "@/components/ui/glass/GlassCard";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { useOnboardingStore } from "@/stores/onboarding";
import { useRouter } from "@/lib/navigation";
import { Check, CreditCard, Lock, Ban } from "lucide-react";
import { cn } from "@/lib/utils";
import { Label } from "@/components/ui/label";

export default function PlanSelection() {
  const { stripe, setStripe, nextStep } = useOnboardingStore();
  const router = useRouter();

  const [enabled, setEnabled] = useState(stripe.enabled);
  const [publicKey, setPublicKey] = useState(stripe.publicKey || "");
  const [secretKey, setSecretKey] = useState(stripe.secretKey || "");
  const [webhookSecret, setWebhookSecret] = useState(stripe.webhookSecret || "");

  const handleContinue = () => {
    setStripe({ enabled, publicKey, secretKey, webhookSecret });
    nextStep();
    router.push("/onboarding/review");
  };

  return (
    <div className="space-y-8 animate-in slide-in-from-right-8 duration-500">

      {/* Option Cards */}
      <div className="grid md:grid-cols-2 gap-4">
        <GlassCard
          variant={!enabled ? "neon" : "default"}
          className={cn(
            "p-6 cursor-pointer hover:border-glass-border transition-all",
            !enabled ? "border-neon-border bg-neon-bg" : "opacity-70"
          )}
          onClick={() => setEnabled(false)}
        >
          <div className="flex items-center gap-3 mb-2">
             <Ban className={cn("w-6 h-6", !enabled ? "text-neon-text" : "text-text-secondary")} />
             <h3 className="text-lg font-bold text-foreground">No Payments</h3>
          </div>
          <p className="text-sm text-text-subtle">
            I don't need to charge users right now. I will manually manage access or use this for internal tools.
          </p>
        </GlassCard>

        <GlassCard
          variant={enabled ? "neon" : "default"}
          className={cn(
            "p-6 cursor-pointer hover:border-glass-border transition-all",
            enabled ? "border-neon-border bg-neon-bg" : "opacity-70"
          )}
          onClick={() => setEnabled(true)}
        >
          <div className="flex items-center gap-3 mb-2">
             <CreditCard className={cn("w-6 h-6", enabled ? "text-neon-text" : "text-text-secondary")} />
             <h3 className="text-lg font-bold text-foreground">Enable Monetization</h3>
          </div>
          <p className="text-sm text-text-subtle">
            I want to sell subscriptions or products. I will connect my Stripe account.
          </p>
        </GlassCard>
      </div>

      {/* Stripe Form (Conditional) */}
      {enabled && (
        <div className="space-y-4 animate-in fade-in slide-in-from-top-4">
            <div className="p-4 bg-warning-bg border border-warning-border rounded-lg text-warning-text text-sm flex gap-2">
                <Lock className="w-4 h-4 shrink-0 mt-0.5" />
                <p>Your API keys will be stored securely in your Tenant configuration. You can find these in your Stripe Dashboard under Developers &gt; API keys.</p>
            </div>

            <div className="space-y-2">
                <Label htmlFor="pk" className="text-foreground">Stripe Publishable Key</Label>
                <GlassInput
                    id="pk"
                    placeholder="pk_live_..."
                    value={publicKey}
                    onChange={(e) => setPublicKey(e.target.value)}
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="sk" className="text-foreground">Stripe Secret Key</Label>
                <GlassInput
                    id="sk"
                    type="password"
                    placeholder="sk_live_..."
                    value={secretKey}
                    onChange={(e) => setSecretKey(e.target.value)}
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="wh" className="text-foreground">Stripe Webhook Secret</Label>
                <GlassInput
                    id="wh"
                    type="password"
                    placeholder="whsec_..."
                    value={webhookSecret}
                    onChange={(e) => setWebhookSecret(e.target.value)}
                />
                <p className="text-xs text-text-tertiary">Used to verify events from Stripe.</p>
            </div>
        </div>
      )}

      <GlassButton
        onClick={handleContinue}
        disabled={enabled && (!publicKey || !secretKey || !webhookSecret)}
        className="w-full"
      >
        Continue
      </GlassButton>
    </div>
  );
}
