"use client";

import React from "react";
import { GlassCard } from "@/components/ui/glass/GlassCard";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { useOnboardingStore } from "@/stores/onboarding";
import { useRouter } from "@/lib/navigation";
import { Check, Loader2 } from "lucide-react";

import { submitOnboarding } from "@/lib/api/onboarding";

export default function ReviewConfirm() {
  const store = useOnboardingStore();
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      await submitOnboarding(store);
      router.push("/dashboard");
    } catch (error) {
      console.error(error);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 animate-in slide-in-from-right-8 duration-500">
      
      <div className="space-y-4">
        {/* User */}
        <div className="bg-white/5 p-4 rounded-xl flex justify-between items-center">
          <div>
            <div className="text-xs text-white/50 uppercase tracking-wider">Profile</div>
            <div className="text-white font-medium">{store.user.firstName} {store.user.lastName}</div>
          </div>
          <Check className="w-5 h-5 text-neon" />
        </div>

        {/* Organization */}
        <div className="bg-white/5 p-4 rounded-xl flex justify-between items-center">
          <div>
            <div className="text-xs text-white/50 uppercase tracking-wider">Workspace</div>
            <div className="text-white font-medium">{store.organization.name}</div>
            <div className="text-xs text-white/30">{store.organization.slug}.acme.dev</div>
          </div>
          <Check className="w-5 h-5 text-neon" />
        </div>

        {/* Billing */}
        <div className="bg-white/5 p-4 rounded-xl flex justify-between items-center border border-neon/30">
          <div>
             <div className="text-xs text-white/50 uppercase tracking-wider">Billing Setup</div>
             <div className="text-white font-medium">
                {store.stripe.enabled ? "Monetization Enabled" : "No Monetization"}
             </div>
             {store.stripe.enabled && (
                <div className="text-xs text-neon mt-1">Stripe Keys Configured</div>
             )}
          </div>
          <Check className="w-5 h-5 text-neon" />
        </div>
      </div>

      <GlassButton 
        onClick={handleSubmit} 
        disabled={isSubmitting}
        variant="primary"
        className="w-full text-lg py-4 h-auto"
      >
        {isSubmitting ? (
          <><Loader2 className="mr-2 h-5 w-5 animate-spin" /> Launching...</>
        ) : (
          "Confirm & Launch Workspace"
        )}
      </GlassButton>
    </div>
  );
}
