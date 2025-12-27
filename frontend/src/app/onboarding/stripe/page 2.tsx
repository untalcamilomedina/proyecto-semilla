"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, ArrowLeft, CreditCard, Check } from "lucide-react";

import { apiPost, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

export default function OnboardingStripePage() {
    const [isConnected, setIsConnected] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const onConnect = async () => {
        // In production, this would redirect to Stripe Connect OAuth
        setIsConnected(true);
    };

    const onContinue = async () => {
        setIsLoading(true);
        setError(null);

        try {
            await apiPost("/api/v1/onboarding/stripe/", { stripe_connected: isConnected });
            router.push("/onboarding/domain");
        } catch (err) {
            if (err instanceof ApiError) {
                setError("Error al guardar configuración");
            } else {
                setError("Error de conexión");
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-zinc-100 px-4 py-12">
            <Card className="w-full max-w-lg">
                <CardHeader className="text-center">
                    <div className="mx-auto w-12 h-12 rounded-xl bg-violet-100 flex items-center justify-center mb-4">
                        <CreditCard className="h-6 w-6 text-violet-600" />
                    </div>
                    <CardTitle className="text-2xl">Conecta Stripe</CardTitle>
                    <CardDescription>
                        Paso 3 de 6 — Configura pagos para tu organización
                    </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                    {error && (
                        <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                            {error}
                        </div>
                    )}

                    <div className="rounded-lg border border-zinc-200 p-6 text-center">
                        {isConnected ? (
                            <div className="space-y-3">
                                <div className="mx-auto w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                                    <Check className="h-6 w-6 text-green-600" />
                                </div>
                                <p className="font-medium text-green-700">Stripe conectado</p>
                                <p className="text-sm text-zinc-500">
                                    Tu cuenta de Stripe está lista para recibir pagos
                                </p>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <p className="text-sm text-zinc-600">
                                    Conecta tu cuenta de Stripe para poder recibir pagos y
                                    gestionar suscripciones.
                                </p>
                                <Button onClick={onConnect} className="w-full">
                                    <CreditCard className="mr-2 h-4 w-4" />
                                    Conectar Stripe
                                </Button>
                            </div>
                        )}
                    </div>

                    <p className="text-xs text-zinc-500 text-center">
                        Puedes configurar esto más tarde si lo prefieres
                    </p>
                </CardContent>

                <CardFooter className="flex gap-3">
                    <Button
                        variant="outline"
                        onClick={() => router.push("/onboarding/modules")}
                    >
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Atrás
                    </Button>
                    <Button className="flex-1" onClick={onContinue} isLoading={isLoading}>
                        {isConnected ? "Continuar" : "Omitir por ahora"}
                        <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                </CardFooter>
            </Card>
        </div>
    );
}
