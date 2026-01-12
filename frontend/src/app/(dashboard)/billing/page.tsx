"use client";

// Skip static generation - requires auth
export const dynamic = "force-dynamic";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import {
    CreditCard,
    Check,
    Loader2,
    Download,
    ExternalLink,
    AlertTriangle,
    Crown,
    Calendar,
    ArrowUpRight,
} from "lucide-react";

import { apiGet, apiPost, apiPatch, ApiError } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { GlassCard } from "@/components/ui/glass/GlassCard";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from "@/components/ui/dialog";
import type { Plan, Subscription, Invoice, PaginatedResponse } from "@/types";
import { cn } from "@/lib/utils";

// Extended types for billing
interface SubscriptionDetail extends Subscription {
    plan: Plan;
}

interface PlanWithPrices extends Plan {
    prices: Array<{
        id: number;
        amount: string;
        currency: string;
        interval: string;
    }>;
}

/**
 * BillingPage
 * Elite billing and subscription management.
 */
export default function BillingPage() {
    const t = useTranslations("billing");
    const tc = useTranslations("common");
    const [confirmCancel, setConfirmCancel] = useState(false);
    const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null);
    const queryClient = useQueryClient();

    // Fetch current subscription
    const { data: subscriptions, isLoading: subscriptionLoading } = useQuery({
        queryKey: ["subscriptions"],
        queryFn: () =>
            apiGet<PaginatedResponse<SubscriptionDetail>>("/api/v1/subscriptions/"),
    });

    const currentSubscription = subscriptions?.results[0];

    // Fetch available plans
    const { data: plans, isLoading: plansLoading } = useQuery({
        queryKey: ["plans"],
        queryFn: () => apiGet<PaginatedResponse<PlanWithPrices>>("/api/v1/plans/"),
    });

    // Fetch invoices
    const { data: invoices, isLoading: invoicesLoading } = useQuery({
        queryKey: ["invoices"],
        queryFn: () => apiGet<PaginatedResponse<Invoice>>("/api/v1/invoices/"),
    });

    // Cancel subscription mutation
    const cancelMutation = useMutation({
        mutationFn: (id: number) =>
            apiPatch(`/api/v1/subscriptions/${id}/`, { cancel_at_period_end: true }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["subscriptions"] });
            setConfirmCancel(false);
        },
    });

    // Upgrade/downgrade mutation (placeholder)
    const changePlanMutation = useMutation({
        mutationFn: ({ subscriptionId, planId }: { subscriptionId: number; planId: number }) =>
            apiPatch(`/api/v1/subscriptions/${subscriptionId}/`, { plan: planId }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["subscriptions"] });
            setSelectedPlan(null);
        },
    });

    const getStatusBadge = (status: string) => {
        const colors: Record<string, string> = {
            active: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
            trialing: "bg-blue-500/10 text-blue-400 border-blue-500/20",
            past_due: "bg-amber-500/10 text-amber-400 border-amber-500/20",
            canceled: "bg-white/5 text-white/40 border-white/10",
            incomplete: "bg-orange-500/10 text-orange-400 border-orange-500/20",
        };
        
        return (
            <span
                className={`inline-flex items-center rounded-lg border px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider ${colors[status] || colors.incomplete}`}
            >
                {t(`status.${status}`)}
            </span>
        );
    };

    const isLoading = subscriptionLoading || plansLoading || invoicesLoading;

    if (isLoading) {
        return (
            <div className="flex justify-center py-20">
                <div className="relative">
                    <div className="absolute inset-0 bg-neon/20 blur-xl rounded-full" />
                    <Loader2 className="h-10 w-10 animate-spin text-neon relative z-10" />
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/20">
                        <CreditCard className="h-6 w-6 text-indigo-400" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white/90">{t("title")}</h1>
                        <p className="text-sm text-white/40">
                            {t("description")}
                        </p>
                    </div>
                </div>
            </div>

            {/* Current Subscription */}
            <GlassCard className="overflow-hidden border-white/5 bg-white/[0.02]">
                <div className="p-6 sm:p-8">
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 mb-8">
                        <div className="flex items-center gap-4">
                            <div className="h-12 w-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20">
                                <Crown className="h-6 w-6 text-indigo-400" />
                            </div>
                            <div>
                                <h3 className="text-lg font-bold text-white/90">{t("currentSubscription")}</h3>
                                <p className="text-white/40 text-sm">
                                    {currentSubscription
                                        ? `${t("plan")} ${currentSubscription.plan?.name || "—"}`
                                        : t("noSubscription")}
                                </p>
                            </div>
                        </div>
                        {currentSubscription && getStatusBadge(currentSubscription.status)}
                    </div>
                    
                    {currentSubscription ? (
                        <div className="grid gap-8 sm:grid-cols-3">
                            <div className="space-y-1">
                                <p className="text-[10px] font-bold uppercase tracking-wider text-white/20">{t("plan")}</p>
                                <p className="text-base font-semibold text-white/80">
                                    {currentSubscription.plan?.name || "—"}
                                </p>
                            </div>
                            <div className="space-y-1">
                                <p className="text-[10px] font-bold uppercase tracking-wider text-white/20">{t("nextInvoice")}</p>
                                <p className="text-base font-semibold text-white/80">
                                    {currentSubscription.current_period_end
                                        ? formatDate(currentSubscription.current_period_end)
                                        : "—"}
                                </p>
                            </div>
                            <div className="space-y-1">
                                <p className="text-[10px] font-bold uppercase tracking-wider text-white/20">{t("users")}</p>
                                <p className="text-base font-semibold text-white/80">
                                    {currentSubscription.quantity}
                                </p>
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center py-8 px-4 rounded-2xl border border-dashed border-white/10 bg-white/[0.01]">
                            <AlertTriangle className="h-8 w-8 text-amber-500/50 mb-3" />
                            <p className="text-white/50 text-center max-w-sm">
                                {t("noSubscription")}
                            </p>
                        </div>
                    )}
                </div>
                
                {currentSubscription && currentSubscription.status === "active" && (
                    <div className="px-8 py-4 bg-white/[0.02] border-t border-white/5 flex items-center justify-between">
                        {currentSubscription.cancel_at_period_end ? (
                            <p className="text-xs text-amber-400 flex items-center gap-2 font-medium">
                                <AlertTriangle className="h-3.5 w-3.5" />
                                {t("willCancelAtEnd")}
                            </p>
                        ) : (
                            <button
                                className="text-xs font-semibold text-white/30 hover:text-red-400 transition-colors"
                                onClick={() => setConfirmCancel(true)}
                            >
                                {t("cancelSubscription")}
                            </button>
                        )}
                        
                        <div className="h-1 w-24 bg-white/5 rounded-full overflow-hidden">
                            <div className="h-full bg-indigo-500/30 w-1/3" />
                        </div>
                    </div>
                )}
            </GlassCard>

            {/* Cancel Confirmation Dialog */}
            <Dialog open={confirmCancel} onOpenChange={setConfirmCancel}>
                <DialogContent className="bg-zinc-900/90 border-white/10 backdrop-blur-xl text-white">
                    <DialogHeader>
                        <DialogTitle className="text-xl font-bold">{t("confirmCancel")}</DialogTitle>
                        <DialogDescription className="text-white/50">
                            {t("cancelDescription")}
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter className="gap-3 sm:gap-0 mt-6">
                        <GlassButton variant="secondary" onClick={() => setConfirmCancel(false)}>
                            {t("keepSubscription")}
                        </GlassButton>
                        <GlassButton
                            variant="danger"
                            disabled={cancelMutation.isPending}
                            onClick={() =>
                                currentSubscription && cancelMutation.mutate(currentSubscription.id)
                            }
                        >
                            {cancelMutation.isPending ? tc("loading") : t("confirmCancellation")}
                        </GlassButton>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Available Plans */}
            <div className="space-y-6">
                <div className="flex items-center gap-3">
                    <div className="h-1 w-8 bg-neon rounded-full" />
                    <h2 className="text-xl font-bold text-white/90">
                        {t("availablePlans")}
                    </h2>
                </div>
                
                {plans?.results.length === 0 ? (
                    <p className="text-sm text-white/30 italic">{t("noPlans")}</p>
                ) : (
                    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {plans?.results.map((plan) => {
                            const isCurrentPlan = currentSubscription?.plan?.id === plan.id;
                            const mainPrice = plan.prices?.[0];

                            return (
                                <GlassCard
                                    key={plan.id}
                                    className={cn(
                                        "group relative flex flex-col hover:border-indigo-500/30 transition-all duration-500",
                                        isCurrentPlan && "border-indigo-500/50 bg-indigo-500/[0.02]"
                                    )}
                                >
                                    {isCurrentPlan && (
                                        <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-indigo-500 text-[10px] font-bold uppercase tracking-widest text-white shadow-lg shadow-indigo-500/20">
                                            {t("current")}
                                        </div>
                                    )}
                                    
                                    <div className="p-8 flex-1 flex flex-col space-y-6">
                                        <div className="space-y-2">
                                            <h3 className="text-xl font-bold text-white group-hover:text-indigo-400 transition-colors">{plan.name}</h3>
                                            <p className="text-sm text-white/40 line-clamp-2 leading-relaxed">
                                                {plan.description}
                                            </p>
                                        </div>

                                        <div className="py-4">
                                            {mainPrice ? (
                                                <div className="flex items-baseline gap-1">
                                                    <span className="text-3xl font-black text-white">
                                                        {formatCurrency(
                                                            parseFloat(mainPrice.amount),
                                                            mainPrice.currency.toUpperCase()
                                                        )}
                                                    </span>
                                                    <span className="text-sm font-medium text-white/30">
                                                        {mainPrice.interval === "month" ? t("perMonth") : t("perYear")}
                                                    </span>
                                                </div>
                                            ) : (
                                                <span className="text-3xl font-black text-white">
                                                    {t("free")}
                                                </span>
                                            )}
                                        </div>

                                        <ul className="space-y-4 flex-1">
                                            {plan.seat_limit && (
                                                <li className="flex items-center gap-3 text-sm text-white/60">
                                                    <div className="h-5 w-5 rounded-full bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
                                                        <Check className="h-3 w-3 text-emerald-400" />
                                                    </div>
                                                    {t("upToUsers", { count: plan.seat_limit })}
                                                </li>
                                            )}
                                            {plan.trial_days > 0 && (
                                                <li className="flex items-center gap-3 text-sm text-white/60">
                                                    <div className="h-5 w-5 rounded-full bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20">
                                                        <Check className="h-3 w-3 text-indigo-400" />
                                                    </div>
                                                    {t("trialDays", { count: plan.trial_days })}
                                                </li>
                                            )}
                                        </ul>

                                        <div className="pt-6">
                                            {isCurrentPlan ? (
                                                <GlassButton variant="secondary" className="w-full opacity-50 cursor-default hover:scale-100 active:scale-100" disabled>
                                                    {t("currentPlan")}
                                                </GlassButton>
                                            ) : (
                                                <GlassButton
                                                    className="w-full group/btn"
                                                    onClick={() => setSelectedPlan(plan)}
                                                >
                                                    <span>{currentSubscription ? t("changePlan") : t("select")}</span>
                                                    <ArrowUpRight className="ml-2 h-4 w-4 group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5 transition-transform" />
                                                </GlassButton>
                                            )}
                                        </div>
                                    </div>
                                </GlassCard>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Change Plan Dialog */}
            <Dialog open={!!selectedPlan} onOpenChange={() => setSelectedPlan(null)}>
                <DialogContent className="bg-zinc-900/90 border-white/10 backdrop-blur-xl text-white">
                    <DialogHeader>
                        <DialogTitle className="text-xl font-bold">{t("changeTo", { name: selectedPlan?.name })}</DialogTitle>
                        <DialogDescription className="text-white/50">
                            {currentSubscription
                                ? t("changeDescription")
                                : t("newPlanDescription")}
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter className="gap-3 sm:gap-0 mt-6">
                        <GlassButton variant="secondary" onClick={() => setSelectedPlan(null)}>
                            {tc("cancel")}
                        </GlassButton>
                        <GlassButton
                            disabled={changePlanMutation.isPending}
                            onClick={() =>
                                selectedPlan &&
                                currentSubscription &&
                                changePlanMutation.mutate({
                                    subscriptionId: currentSubscription.id,
                                    planId: selectedPlan.id,
                                })
                            }
                        >
                            {changePlanMutation.isPending ? tc("loading") : t("confirmChange")}
                        </GlassButton>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Invoices */}
            <div className="space-y-6">
                <div className="flex items-center gap-3">
                    <div className="h-1 w-8 bg-indigo-500 rounded-full" />
                    <h2 className="text-xl font-bold text-white/90">
                        {t("invoiceHistory")}
                    </h2>
                </div>
                
                <GlassCard className="overflow-hidden border-white/5">
                    {invoices?.results.length === 0 ? (
                        <div className="p-12 text-center space-y-4">
                            <div className="p-6 rounded-full bg-white/5 inline-block">
                                <CreditCard className="h-10 w-10 text-white/10" />
                            </div>
                            <p className="text-white/30 font-medium">
                                {t("noInvoices")}
                            </p>
                        </div>
                    ) : (
                        <div className="divide-y divide-white/5">
                            {invoices?.results.map((invoice) => (
                                <div
                                    key={invoice.id}
                                    className="flex flex-col sm:flex-row sm:items-center justify-between p-6 gap-6 hover:bg-white/[0.02] transition-colors group"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className="h-11 w-11 rounded-2xl bg-white/5 flex items-center justify-center border border-white/10 group-hover:scale-110 transition-transform duration-500">
                                            <Calendar className="h-5 w-5 text-white/40" />
                                        </div>
                                        <div>
                                            <p className="text-sm font-bold text-white/80">
                                                {formatDate(invoice.created_at)}
                                            </p>
                                            <p className="text-xs text-white/30 font-mono tracking-tight">
                                                {invoice.stripe_invoice_id}
                                            </p>
                                        </div>
                                    </div>
                                    
                                    <div className="flex items-center justify-between sm:justify-end gap-8">
                                        <div className="text-right">
                                            <p className="text-base font-black text-white">
                                                {formatCurrency(
                                                    parseFloat(invoice.amount_paid),
                                                    invoice.currency.toUpperCase()
                                                )}
                                            </p>
                                            <p className="text-[10px] font-bold uppercase tracking-wider text-emerald-400/70">
                                                {invoice.status === "paid" ? t("paid") : invoice.status}
                                            </p>
                                        </div>
                                        <div className="flex gap-2">
                                            {invoice.hosted_invoice_url && (
                                                <button
                                                    className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-white/40 hover:text-white transition-all transform hover:scale-110 border border-white/10"
                                                    title="View"
                                                    onClick={() => window.open(invoice.hosted_invoice_url, "_blank")}
                                                >
                                                    <ExternalLink className="h-4 w-4" />
                                                </button>
                                            )}
                                            {invoice.invoice_pdf && (
                                                <button
                                                    className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-white/40 hover:text-white transition-all transform hover:scale-110 border border-white/10"
                                                    title="Download"
                                                    onClick={() => window.open(invoice.invoice_pdf, "_blank")}
                                                >
                                                    <Download className="h-4 w-4" />
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </GlassCard>
            </div>
        </div>
    );
}
