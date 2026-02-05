"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { CreditCard, CheckCircle, AlertCircle } from "lucide-react";
import { apiGet } from "@/lib/api";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

// Define strict types for billing data
interface SubscriptionData {
    plan_code: string; // 'free', 'pro', etc.
    status: string;
    diagrams_used: number;
    diagrams_limit: number;
    requests_used: number;
    requests_limit: number;
}

export default function BillingPage() {
    const t = useTranslations("billing");
    const [subscription, setSubscription] = useState<SubscriptionData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchBilling = async () => {
            try {
                // Determine appropriate endpoint. 
                // The task.md says "UsageMetering" is implemented.
                // Assuming /api/v1/billing/subscription/ returns this structure based on previous audits.
                const data = await apiGet<SubscriptionData>("/api/v1/billing/subscription/");
                setSubscription(data);
            } catch (error) {
                console.error("Failed to load billing", error);
            } finally {
                setLoading(false);
            }
        };
        fetchBilling();
    }, []);

    const handleUpgrade = (plan: string) => {
        alert(`Upgrade to ${plan} logic goes here (Stripe Integration)`);
    };

    if (loading) {
        return <div className="p-8 text-white">Loading billing info...</div>;
    }

    if (!subscription) {
        return <div className="p-8 text-red-400">Failed to load subscription.</div>;
    }

    const diagramsParams = {
        percent: Math.min((subscription.diagrams_used / subscription.diagrams_limit) * 100, 100),
        label: `${subscription.diagrams_used} / ${subscription.diagrams_limit}`
    };

    return (
        <div className="container max-w-5xl py-10 space-y-10">
            {/* Header */}
            <div className="space-y-2">
                <h1 className="text-3xl font-bold text-white glow-text">{t("title")}</h1>
                <p className="text-white/60 text-lg">{t("description")}</p>
            </div>

            {/* Current Plan & Usage */}
            <div className="grid md:grid-cols-2 gap-6">
                <GlassCard className="space-y-6">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-purple-500/20 rounded-xl">
                             <CreditCard className="w-8 h-8 text-purple-400" />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-white uppercase tracking-wider">
                                {subscription.plan_code} PLAN
                            </h3>
                            <div className="flex items-center gap-2 text-sm text-green-400 mt-1">
                                <CheckCircle className="w-4 h-4" />
                                <span className="uppercase">{subscription.status}</span>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-white/70">Diagrams Used</span>
                                <span className="text-white font-mono">{diagramsParams.label}</span>
                            </div>
                            <Progress value={diagramsParams.percent} className="h-2" />
                        </div>
                         {/* Requests limit might be huge, handled differently? Assuming basic implementation */}
                        <div className="space-y-2">
                             <div className="flex justify-between text-sm">
                                <span className="text-white/70">AI Requests</span>
                                <span className="text-white font-mono">{subscription.requests_used} / {subscription.requests_limit}</span>
                            </div>
                            <Progress value={(subscription.requests_used / subscription.requests_limit) * 100} className="h-2" />
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="flex flex-col justify-center items-center text-center space-y-4 bg-gradient-to-br from-white/5 to-purple-500/5">
                     <h3 className="text-2xl font-bold text-white">Need more power?</h3>
                     <p className="text-white/60 max-w-xs">
                        Upgrade to Pro to unlock unlimited diagrams and advanced AI features.
                     </p>
                     <Button 
                        className="bg-purple-500 hover:bg-purple-600 text-white px-8"
                        onClick={() => handleUpgrade('pro')}
                    >
                        Upgrade Now
                     </Button>
                </GlassCard>
            </div>

            {/* Plans Table (Mock) */}
            <h2 className="text-2xl font-bold text-white">Available Plans</h2>
            <div className="grid md:grid-cols-3 gap-6">
                 {/* Free */}
                 <GlassCard className="border-t-4 border-t-gray-500 flex flex-col gap-4">
                     <div>
                        <h3 className="text-xl font-bold">Free</h3>
                        <div className="text-3xl font-bold mt-2">$0<span className="text-sm font-normal text-white/50">/mo</span></div>
                     </div>
                     <ul className="space-y-2 text-sm text-white/70 flex-1">
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-green-400"/> 5 Diagrams</li>
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-green-400"/> Basic AI Gen</li>
                     </ul>
                     <Button variant="outline" disabled className="w-full border-white/10 text-white/50">Current Plan</Button>
                 </GlassCard>

                 {/* Pro */}
                 <GlassCard className="border-t-4 border-t-purple-500 bg-purple-500/5 flex flex-col gap-4 relative">
                     <div className="absolute top-0 right-0 p-2 text-xs bg-purple-500 text-white font-bold rounded-bl-xl">POPULAR</div>
                     <div>
                        <h3 className="text-xl font-bold text-purple-400">Pro</h3>
                        <div className="text-3xl font-bold mt-2">$29<span className="text-sm font-normal text-white/50">/mo</span></div>
                     </div>
                     <ul className="space-y-2 text-sm text-white/70 flex-1">
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-purple-400"/> Unlimited Diagrams</li>
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-purple-400"/> Advanced AI (Gemini Pro)</li>
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-purple-400"/> Priority Support</li>
                     </ul>
                     <Button className="w-full bg-purple-500 hover:bg-purple-600" onClick={() => handleUpgrade('pro')}>Upgrade</Button>
                 </GlassCard>

                  {/* Enterprise */}
                 <GlassCard className="border-t-4 border-t-blue-500 flex flex-col gap-4">
                     <div>
                        <h3 className="text-xl font-bold text-blue-400">Enterprise</h3>
                        <div className="text-3xl font-bold mt-2">Custom</div>
                     </div>
                     <ul className="space-y-2 text-sm text-white/70 flex-1">
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-blue-400"/> SSO & Audit Logs</li>
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-blue-400"/> Custom AI Models</li>
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-blue-400"/> SLA Guarantee</li>
                     </ul>
                     <Button variant="outline" className="w-full border-white/20 hover:bg-white/10" onClick={() => handleUpgrade('enterprise')}>Contact Sales</Button>
                 </GlassCard>
            </div>
        </div>
    );
}
