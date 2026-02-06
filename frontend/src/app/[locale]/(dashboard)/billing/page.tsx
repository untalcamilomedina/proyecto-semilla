"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { CreditCard, CheckCircle } from "lucide-react";
import { apiGet } from "@/lib/api";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface SubscriptionData {
    plan_code: string;
    status: string;
    diagrams_used: number;
    diagrams_limit: number;
    requests_used: number;
    requests_limit: number;
}

export default function BillingPage() {
    const t = useTranslations("billing");
    const tc = useTranslations("common");
    const [subscription, setSubscription] = useState<SubscriptionData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchBilling = async () => {
            try {
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
        // TODO: Integrate with Stripe checkout
        console.log(`Upgrade to ${plan}`);
    };

    if (loading) {
        return <div className="p-8 text-foreground">{t("loadingBilling")}</div>;
    }

    if (!subscription) {
        return <div className="p-8 text-error-text">{t("failedToLoad")}</div>;
    }

    const diagramsPercent = Math.min((subscription.diagrams_used / subscription.diagrams_limit) * 100, 100);
    const requestsPercent = (subscription.requests_used / subscription.requests_limit) * 100;

    return (
        <div className="container max-w-5xl py-10 space-y-10">
            <div className="space-y-2">
                <h1 className="text-3xl font-bold text-foreground">{t("title")}</h1>
                <p className="text-text-subtle text-lg">{t("description")}</p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                <GlassCard className="space-y-6">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-purple-500/20 rounded-xl">
                             <CreditCard className="w-8 h-8 text-purple-400" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-foreground uppercase tracking-wider">
                                {t("planLabel", { plan: subscription.plan_code.toUpperCase() })}
                            </h2>
                            <div className="flex items-center gap-2 text-sm text-success-text mt-1">
                                <CheckCircle className="w-4 h-4" />
                                <span className="uppercase">{t(`status.${subscription.status}`)}</span>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-text-subtle">{t("diagramsUsed")}</span>
                                <span className="text-foreground font-mono">{subscription.diagrams_used} / {subscription.diagrams_limit}</span>
                            </div>
                            <Progress value={diagramsPercent} className="h-2" />
                        </div>
                        <div className="space-y-2">
                             <div className="flex justify-between text-sm">
                                <span className="text-text-subtle">{t("aiRequests")}</span>
                                <span className="text-foreground font-mono">{subscription.requests_used} / {subscription.requests_limit}</span>
                            </div>
                            <Progress value={requestsPercent} className="h-2" />
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="flex flex-col justify-center items-center text-center space-y-4 bg-gradient-to-br from-glass-bg to-purple-500/5">
                     <h2 className="text-2xl font-bold text-foreground">{t("needMorePower")}</h2>
                     <p className="text-text-subtle max-w-xs">
                        {t("upgradeDescription")}
                     </p>
                     <Button
                        className="bg-purple-500 hover:bg-purple-600 text-foreground px-8"
                        onClick={() => handleUpgrade('pro')}
                    >
                        {t("upgradeNow")}
                     </Button>
                </GlassCard>
            </div>

            <h2 className="text-2xl font-bold text-foreground">{t("availablePlans")}</h2>
            <div className="grid md:grid-cols-3 gap-6">
                 <GlassCard className="border-t-4 border-t-gray-500 flex flex-col gap-4">
                     <div>
                        <h3 className="text-xl font-bold">{t("free")}</h3>
                        <div className="text-3xl font-bold mt-2">$0<span className="text-sm font-normal text-text-secondary">{t("perMonth")}</span></div>
                     </div>
                     <ul className="space-y-2 text-sm text-text-subtle flex-1">
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-success-text"/> {t("features.diagrams5")}</li>
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-success-text"/> {t("features.basicAI")}</li>
                     </ul>
                     <Button variant="outline" disabled className="w-full border-glass-border text-text-secondary">{t("currentPlan")}</Button>
                 </GlassCard>

                 <GlassCard className="border-t-4 border-t-purple-500 bg-purple-500/5 flex flex-col gap-4 relative">
                     <div className="absolute top-0 right-0 p-2 text-xs bg-purple-500 text-white font-bold rounded-bl-xl">{t("popular")}</div>
                     <div>
                        <h3 className="text-xl font-bold text-purple-400">{t("pro")}</h3>
                        <div className="text-3xl font-bold mt-2">$29<span className="text-sm font-normal text-text-secondary">{t("perMonth")}</span></div>
                     </div>
                     <ul className="space-y-2 text-sm text-text-subtle flex-1">
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-purple-400"/> {t("features.unlimitedDiagrams")}</li>
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-purple-400"/> {t("features.advancedAI")}</li>
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-purple-400"/> {t("features.prioritySupport")}</li>
                     </ul>
                     <Button className="w-full bg-purple-500 hover:bg-purple-600" onClick={() => handleUpgrade('pro')}>{t("upgrade")}</Button>
                 </GlassCard>

                 <GlassCard className="border-t-4 border-t-blue-500 flex flex-col gap-4">
                     <div>
                        <h3 className="text-xl font-bold text-blue-400">{t("enterprise")}</h3>
                        <div className="text-3xl font-bold mt-2">{t("custom")}</div>
                     </div>
                     <ul className="space-y-2 text-sm text-text-subtle flex-1">
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-blue-400"/> {t("features.sso")}</li>
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-blue-400"/> {t("features.customModels")}</li>
                        <li className="flex gap-2"><CheckCircle className="w-4 h-4 text-blue-400"/> {t("features.sla")}</li>
                     </ul>
                     <Button variant="outline" className="w-full border-glass-border hover:bg-glass-bg-hover" onClick={() => handleUpgrade('enterprise')}>{t("contactSales")}</Button>
                 </GlassCard>
            </div>
        </div>
    );
}
