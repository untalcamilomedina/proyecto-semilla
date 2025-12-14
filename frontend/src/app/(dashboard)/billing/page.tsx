"use client";

// Skip static generation - requires auth
export const dynamic = "force-dynamic";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
    CreditCard,
    Check,
    Loader2,
    Download,
    ExternalLink,
    AlertTriangle,
    Crown,
    Calendar,
} from "lucide-react";

import { apiGet, apiPost, apiPatch, ApiError } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from "@/components/ui/dialog";
import type { Plan, Subscription, Invoice, PaginatedResponse } from "@/types";

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

export default function BillingPage() {
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
            active: "bg-green-100 text-green-700",
            trialing: "bg-blue-100 text-blue-700",
            past_due: "bg-yellow-100 text-yellow-700",
            canceled: "bg-zinc-100 text-zinc-600",
            incomplete: "bg-orange-100 text-orange-700",
        };
        const labels: Record<string, string> = {
            active: "Activa",
            trialing: "Prueba",
            past_due: "Pago pendiente",
            canceled: "Cancelada",
            incomplete: "Incompleta",
        };
        return (
            <span
                className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[status] || colors.incomplete}`}
            >
                {labels[status] || status}
            </span>
        );
    };

    const isLoading = subscriptionLoading || plansLoading || invoicesLoading;

    if (isLoading) {
        return (
            <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-zinc-400" />
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-zinc-900">Facturación</h1>
                <p className="mt-1 text-sm text-zinc-500">
                    Gestiona tu suscripción, planes y facturas
                </p>
            </div>

            {/* Current Subscription */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-lg bg-indigo-100 flex items-center justify-center">
                                <Crown className="h-5 w-5 text-indigo-600" />
                            </div>
                            <div>
                                <CardTitle className="text-lg">Suscripción actual</CardTitle>
                                <CardDescription>
                                    {currentSubscription
                                        ? `Plan ${currentSubscription.plan?.name || "—"}`
                                        : "Sin suscripción activa"}
                                </CardDescription>
                            </div>
                        </div>
                        {currentSubscription && getStatusBadge(currentSubscription.status)}
                    </div>
                </CardHeader>
                <CardContent>
                    {currentSubscription ? (
                        <div className="grid gap-4 sm:grid-cols-3">
                            <div>
                                <p className="text-xs font-medium text-zinc-500">Plan</p>
                                <p className="text-sm font-semibold text-zinc-900">
                                    {currentSubscription.plan?.name || "—"}
                                </p>
                            </div>
                            <div>
                                <p className="text-xs font-medium text-zinc-500">Próxima factura</p>
                                <p className="text-sm font-semibold text-zinc-900">
                                    {currentSubscription.current_period_end
                                        ? formatDate(currentSubscription.current_period_end)
                                        : "—"}
                                </p>
                            </div>
                            <div>
                                <p className="text-xs font-medium text-zinc-500">Usuarios</p>
                                <p className="text-sm font-semibold text-zinc-900">
                                    {currentSubscription.quantity}
                                </p>
                            </div>
                        </div>
                    ) : (
                        <div className="flex items-center gap-3 rounded-lg border border-dashed border-zinc-200 p-4">
                            <AlertTriangle className="h-5 w-5 text-amber-500" />
                            <p className="text-sm text-zinc-600">
                                No tienes una suscripción activa. Selecciona un plan para comenzar.
                            </p>
                        </div>
                    )}
                </CardContent>
                {currentSubscription && currentSubscription.status === "active" && (
                    <CardFooter className="border-t border-zinc-100 pt-4">
                        {currentSubscription.cancel_at_period_end ? (
                            <p className="text-sm text-amber-600 flex items-center gap-2">
                                <AlertTriangle className="h-4 w-4" />
                                Se cancelará al final del período
                            </p>
                        ) : (
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setConfirmCancel(true)}
                            >
                                Cancelar suscripción
                            </Button>
                        )}
                    </CardFooter>
                )}
            </Card>

            {/* Cancel Confirmation Dialog */}
            <Dialog open={confirmCancel} onOpenChange={setConfirmCancel}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>¿Cancelar suscripción?</DialogTitle>
                        <DialogDescription>
                            Tu suscripción permanecerá activa hasta el final del período actual.
                            No se realizarán más cobros.
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setConfirmCancel(false)}>
                            Mantener suscripción
                        </Button>
                        <Button
                            variant="destructive"
                            isLoading={cancelMutation.isPending}
                            onClick={() =>
                                currentSubscription && cancelMutation.mutate(currentSubscription.id)
                            }
                        >
                            Confirmar cancelación
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Available Plans */}
            <div>
                <h2 className="text-lg font-semibold text-zinc-900 mb-4">
                    Planes disponibles
                </h2>
                {plans?.results.length === 0 ? (
                    <p className="text-sm text-zinc-500">No hay planes disponibles.</p>
                ) : (
                    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                        {plans?.results.map((plan) => {
                            const isCurrentPlan = currentSubscription?.plan?.id === plan.id;
                            const mainPrice = plan.prices?.[0];

                            return (
                                <Card
                                    key={plan.id}
                                    className={isCurrentPlan ? "ring-2 ring-indigo-500" : ""}
                                >
                                    <CardHeader>
                                        <div className="flex items-center justify-between">
                                            <CardTitle className="text-base">{plan.name}</CardTitle>
                                            {isCurrentPlan && (
                                                <span className="inline-flex items-center rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700">
                                                    Actual
                                                </span>
                                            )}
                                        </div>
                                        <CardDescription>{plan.description}</CardDescription>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="mb-4">
                                            {mainPrice ? (
                                                <div className="flex items-baseline">
                                                    <span className="text-3xl font-bold text-zinc-900">
                                                        {formatCurrency(
                                                            parseFloat(mainPrice.amount),
                                                            mainPrice.currency.toUpperCase()
                                                        )}
                                                    </span>
                                                    <span className="text-sm text-zinc-500 ml-1">
                                                        /{mainPrice.interval === "month" ? "mes" : "año"}
                                                    </span>
                                                </div>
                                            ) : (
                                                <span className="text-2xl font-bold text-zinc-900">
                                                    Gratis
                                                </span>
                                            )}
                                        </div>
                                        <ul className="space-y-2">
                                            {plan.seat_limit && (
                                                <li className="flex items-center gap-2 text-sm text-zinc-600">
                                                    <Check className="h-4 w-4 text-green-500" />
                                                    Hasta {plan.seat_limit} usuarios
                                                </li>
                                            )}
                                            {plan.trial_days > 0 && (
                                                <li className="flex items-center gap-2 text-sm text-zinc-600">
                                                    <Check className="h-4 w-4 text-green-500" />
                                                    {plan.trial_days} días de prueba
                                                </li>
                                            )}
                                        </ul>
                                    </CardContent>
                                    <CardFooter>
                                        {isCurrentPlan ? (
                                            <Button variant="secondary" className="w-full" disabled>
                                                Plan actual
                                            </Button>
                                        ) : (
                                            <Button
                                                variant="default"
                                                className="w-full"
                                                onClick={() => setSelectedPlan(plan)}
                                            >
                                                {currentSubscription ? "Cambiar plan" : "Seleccionar"}
                                            </Button>
                                        )}
                                    </CardFooter>
                                </Card>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Change Plan Dialog */}
            <Dialog open={!!selectedPlan} onOpenChange={() => setSelectedPlan(null)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Cambiar a {selectedPlan?.name}</DialogTitle>
                        <DialogDescription>
                            {currentSubscription
                                ? "Tu suscripción se actualizará inmediatamente."
                                : "Comenzarás con el nuevo plan seleccionado."}
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setSelectedPlan(null)}>
                            Cancelar
                        </Button>
                        <Button
                            isLoading={changePlanMutation.isPending}
                            onClick={() =>
                                selectedPlan &&
                                currentSubscription &&
                                changePlanMutation.mutate({
                                    subscriptionId: currentSubscription.id,
                                    planId: selectedPlan.id,
                                })
                            }
                        >
                            Confirmar cambio
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Invoices */}
            <div>
                <h2 className="text-lg font-semibold text-zinc-900 mb-4">
                    Historial de facturas
                </h2>
                <Card>
                    <CardContent className="p-0">
                        {invoices?.results.length === 0 ? (
                            <div className="p-6 text-center">
                                <CreditCard className="mx-auto h-8 w-8 text-zinc-300" />
                                <p className="mt-2 text-sm text-zinc-500">
                                    No hay facturas todavía
                                </p>
                            </div>
                        ) : (
                            <div className="divide-y divide-zinc-200">
                                {invoices?.results.map((invoice) => (
                                    <div
                                        key={invoice.id}
                                        className="flex items-center justify-between p-4"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="h-9 w-9 rounded-lg bg-zinc-100 flex items-center justify-center">
                                                <Calendar className="h-4 w-4 text-zinc-500" />
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-zinc-900">
                                                    {formatDate(invoice.created_at)}
                                                </p>
                                                <p className="text-xs text-zinc-500">
                                                    {invoice.stripe_invoice_id}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-4">
                                            <div className="text-right">
                                                <p className="text-sm font-medium text-zinc-900">
                                                    {formatCurrency(
                                                        parseFloat(invoice.amount_paid),
                                                        invoice.currency.toUpperCase()
                                                    )}
                                                </p>
                                                <p className="text-xs text-zinc-500">
                                                    {invoice.status === "paid" ? "Pagada" : invoice.status}
                                                </p>
                                            </div>
                                            <div className="flex gap-1">
                                                {invoice.hosted_invoice_url && (
                                                    <Button
                                                        variant="ghost"
                                                        size="icon"
                                                        asChild
                                                    >
                                                        <a
                                                            href={invoice.hosted_invoice_url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                        >
                                                            <ExternalLink className="h-4 w-4" />
                                                        </a>
                                                    </Button>
                                                )}
                                                {invoice.invoice_pdf && (
                                                    <Button
                                                        variant="ghost"
                                                        size="icon"
                                                        asChild
                                                    >
                                                        <a
                                                            href={invoice.invoice_pdf}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                        >
                                                            <Download className="h-4 w-4" />
                                                        </a>
                                                    </Button>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
