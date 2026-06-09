"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { CreditCard, CheckCircle, ExternalLink, Loader2 } from "lucide-react";
import { apiPost } from "@/lib/api";
import { useResourceQuery } from "@/hooks/use-api";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";

interface PlanPrice {
    id: number;
    currency: string;
    amount: string;
    interval: string;
    interval_count: number;
    is_active: boolean;
}

interface Plan {
    id: number;
    code: string;
    name: string;
    description: string;
    seat_limit: number | null;
    max_items: number;
    max_requests: number;
    trial_days: number;
    prices: PlanPrice[];
}

interface SubscriptionData {
    id: number;
    plan: Plan;
    status: string;
    quantity: number;
    cancel_at_period_end: boolean;
    current_period_end: string | null;
    trial_end: string | null;
    usage?: {
        items_used: number;
        max_items: number;
        requests_used: number;
        max_requests: number;
    };
}

interface PaginatedPlans {
    results: Plan[];
}

export default function BillingPage() {
    const t = useTranslations("billing");
    const [redirecting, setRedirecting] = useState(false);

    const { data: subscription, isLoading: subLoading, error: subError } = useResourceQuery<SubscriptionData>(
        ["billing", "subscription"],
        "/api/v1/subscriptions/current/"
    );
    const { data: plansData, isLoading: plansLoading } = useResourceQuery<PaginatedPlans>(
        ["billing", "plans"],
        "/api/v1/plans/"
    );

    const handleCheckout = async (priceId: number) => {
        setRedirecting(true);
        try {
            const { url } = await apiPost<{ url: string }>("/api/v1/subscriptions/checkout/", {
                price_id: priceId,
            });
            window.location.href = url;
        } catch {
            toast.error(t("checkoutError"));
            setRedirecting(false);
        }
    };

    const handlePortal = async () => {
        setRedirecting(true);
        try {
            const { url } = await apiPost<{ url: string }>("/api/v1/subscriptions/portal/");
            window.location.href = url;
        } catch {
            toast.error(t("portalError"));
            setRedirecting(false);
        }
    };

    if (subLoading || plansLoading) {
        return <div className="p-8 text-foreground">{t("loadingBilling")}</div>;
    }

    const usage = subscription?.usage;
    const itemsPercent = usage && usage.max_items > 0
        ? Math.min((usage.items_used / usage.max_items) * 100, 100)
        : 0;
    const requestsPercent = usage && usage.max_requests > 0
        ? Math.min((usage.requests_used / usage.max_requests) * 100, 100)
        : 0;
    const plans = plansData?.results ?? [];

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
                                {subscription
                                    ? t("planLabel", { plan: subscription.plan.name })
                                    : t("noSubscription")}
                            </h2>
                            {subscription && (
                                <div className="flex items-center gap-2 text-sm text-success-text mt-1">
                                    <CheckCircle className="w-4 h-4" />
                                    <span className="uppercase">{subscription.status}</span>
                                </div>
                            )}
                            {subError != null && !subscription && (
                                <p className="text-sm text-text-subtle mt-1">{t("noSubscriptionHint")}</p>
                            )}
                        </div>
                    </div>

                    {usage && (
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-text-subtle">{t("itemsUsed")}</span>
                                    <span className="text-foreground font-mono">{usage.items_used} / {usage.max_items}</span>
                                </div>
                                <Progress value={itemsPercent} className="h-2" />
                            </div>
                            <div className="space-y-2">
                                 <div className="flex justify-between text-sm">
                                    <span className="text-text-subtle">{t("apiRequests")}</span>
                                    <span className="text-foreground font-mono">{usage.requests_used} / {usage.max_requests}</span>
                                </div>
                                <Progress value={requestsPercent} className="h-2" />
                            </div>
                        </div>
                    )}
                </GlassCard>

                <GlassCard className="flex flex-col justify-center items-center text-center space-y-4 bg-gradient-to-br from-glass-bg to-purple-500/5">
                     <h2 className="text-2xl font-bold text-foreground">{t("manageSubscription")}</h2>
                     <p className="text-text-subtle max-w-xs">
                        {t("portalDescription")}
                     </p>
                     <Button
                        className="bg-purple-500 hover:bg-purple-600 text-foreground px-8"
                        onClick={handlePortal}
                        disabled={redirecting || !subscription}
                    >
                        {redirecting
                            ? <Loader2 className="w-4 h-4 animate-spin" />
                            : <span className="flex items-center gap-2">{t("openPortal")} <ExternalLink className="w-4 h-4" /></span>}
                     </Button>
                </GlassCard>
            </div>

            <h2 className="text-2xl font-bold text-foreground">{t("availablePlans")}</h2>
            {plans.length === 0 ? (
                <GlassCard className="p-8 text-center text-text-subtle">
                    {t("noPlans")}
                </GlassCard>
            ) : (
                <div className="grid md:grid-cols-3 gap-6">
                    {plans.map((plan) => {
                        const price = plan.prices.find((p) => p.is_active);
                        const isCurrent = subscription?.plan.code === plan.code;
                        return (
                            <GlassCard key={plan.id} className="border-t-4 border-t-purple-500 flex flex-col gap-4">
                                <div>
                                    <h3 className="text-xl font-bold">{plan.name}</h3>
                                    <div className="text-3xl font-bold mt-2">
                                        {price ? `$${price.amount}` : t("custom")}
                                        {price && (
                                            <span className="text-sm font-normal text-text-secondary">
                                                /{price.interval}
                                            </span>
                                        )}
                                    </div>
                                </div>
                                <ul className="space-y-2 text-sm text-text-subtle flex-1">
                                    {plan.description && <li>{plan.description}</li>}
                                    <li className="flex gap-2">
                                        <CheckCircle className="w-4 h-4 text-success-text"/>
                                        {t("planItems", { count: plan.max_items })}
                                    </li>
                                    <li className="flex gap-2">
                                        <CheckCircle className="w-4 h-4 text-success-text"/>
                                        {t("planRequests", { count: plan.max_requests })}
                                    </li>
                                    {plan.seat_limit != null && (
                                        <li className="flex gap-2">
                                            <CheckCircle className="w-4 h-4 text-success-text"/>
                                            {t("planSeats", { count: plan.seat_limit })}
                                        </li>
                                    )}
                                </ul>
                                {isCurrent ? (
                                    <Button variant="outline" disabled className="w-full border-glass-border text-text-secondary">
                                        {t("currentPlan")}
                                    </Button>
                                ) : (
                                    <Button
                                        className="w-full bg-purple-500 hover:bg-purple-600"
                                        disabled={!price || redirecting}
                                        onClick={() => price && handleCheckout(price.id)}
                                    >
                                        {t("upgrade")}
                                    </Button>
                                )}
                            </GlassCard>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
