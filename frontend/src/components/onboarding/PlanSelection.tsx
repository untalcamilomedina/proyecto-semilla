"use client";

import React, { useState } from "react";
import { GlassCard } from "@/components/ui/glass/GlassCard";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { useOnboardingStore } from "@/stores/onboarding";
import { useRouter } from "next/navigation";
import { Check, CreditCard, Lock, Ban } from "lucide-react";
import { cn } from "@/lib/utils";
import { Label } from "@/components/ui/label";

export default function PlanSelection() {
  const { stripe, setStripe, nextStep } = useOnboardingStore();
  const router = useRouter();
  
  // Local state for the toggle before saving to store
  const [enabled, setEnabled] = useState(stripe.enabled);
  const [publicKey, setPublicKey] = useState(stripe.publicKey || "");
  const [secretKey, setSecretKey] = useState(stripe.secretKey || "");
  const [webhookSecret, setWebhookSecret] = useState(stripe.webhookSecret || "");

  const handleContinue = () => {
    setStripe({ enabled, publicKey, secretKey, webhookSecret });
    nextStep();
    router.push("/onboarding/review");
  };
  
  // Note: effectively skipping Payment Method step if we are the OWNER setting up Stripe.
  // The original "Payment" step was for US to pay for the SaaS.
  // If we are self-hosting, we don't pay. So we should probably skip /payment too?
  // User said "allows them to connect their stripe".
  // Let's assume step 4 (Payment) is now redundant or can be used for something else.
  // For now, I will redirect to /payment but maybe /payment should be a "Summary" or "Review"?
  // Actually, let's keep it simple: Update Store -> Next.

  return (
    <div className="space-y-8 animate-in slide-in-from-right-8 duration-500">
      
      {/* Option Cards */}
      <div className="grid md:grid-cols-2 gap-4">
        <GlassCard
          variant={!enabled ? "neon" : "default"}
          className={cn(
            "p-6 cursor-pointer hover:border-white/20 transition-all",
            !enabled ? "border-neon/50 bg-neon/10" : "opacity-70"
          )}
          onClick={() => setEnabled(false)}
        >
          <div className="flex items-center gap-3 mb-2">
             <Ban className={cn("w-6 h-6", !enabled ? "text-neon" : "text-white/50")} />
             <h3 className="text-lg font-bold text-white">No Payments</h3>
          </div>
          <p className="text-sm text-white/60">
            I don't need to charge users right now. I will manually manage access or use this for internal tools.
          </p>
        </GlassCard>

        <GlassCard
          variant={enabled ? "neon" : "default"}
          className={cn(
            "p-6 cursor-pointer hover:border-white/20 transition-all",
            enabled ? "border-neon/50 bg-neon/10" : "opacity-70"
          )}
          onClick={() => setEnabled(true)}
        >
          <div className="flex items-center gap-3 mb-2">
             <CreditCard className={cn("w-6 h-6", enabled ? "text-neon" : "text-white/50")} />
             <h3 className="text-lg font-bold text-white">Enable Monetization</h3>
          </div>
          <p className="text-sm text-white/60">
            I want to sell subscriptions or products. I will connect my Stripe account.
          </p>
        </GlassCard>
      </div>

      {/* Stripe Form (Conditional) */}
      {enabled && (
        <div className="space-y-4 animate-in fade-in slide-in-from-top-4">
            <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg text-amber-200 text-sm flex gap-2">
                <Lock className="w-4 h-4 shrink-0 mt-0.5" />
                <p>Your API keys will be stored securely in your Tenant configuration. You can find these in your Stripe Dashboard under Developers &gt; API keys.</p>
            </div>

            <div className="space-y-2">
                <Label htmlFor="pk" className="text-white">Stripe Publishable Key</Label>
                <GlassInput 
                    id="pk" 
                    placeholder="pk_live_..." 
                    value={publicKey} 
                    onChange={(e) => setPublicKey(e.target.value)}
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="sk" className="text-white">Stripe Secret Key</Label>
                <GlassInput 
                    id="sk" 
                    type="password" 
                    placeholder="sk_live_..." 
                    value={secretKey} 
                    onChange={(e) => setSecretKey(e.target.value)}
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="wh" className="text-white">Stripe Webhook Secret</Label>
                <GlassInput 
                    id="wh" 
                    type="password" 
                    placeholder="whsec_..." 
                    value={webhookSecret} 
                    onChange={(e) => setWebhookSecret(e.target.value)}
                />
                <p className="text-xs text-white/40">Used to verify events from Stripe.</p>
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
