"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, ArrowRight, CreditCard } from "lucide-react";

import { apiPost, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

export default function OnboardingStripePage() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const onSkip = async () => {
        setIsLoading(true);
        try {
            await apiPost("/api/v1/onboarding/stripe/", { stripe_connected: false });
            router.push("/onboarding/domain");
        } catch (err) {
            setError("Error al saltar este paso");
            setIsLoading(false);
        }
    };

    const onConnect = async () => {
        setIsLoading(true);
        try {
            // In a real app, this would redirect to Stripe OAuth
            // For now, we simulate success
            await apiPost("/api/v1/onboarding/stripe/", { stripe_connected: true });
            router.push("/onboarding/domain");
        } catch (err) {
            setError("Error al conectar con Stripe");
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-zinc-100 px-4 py-12">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <div className="mx-auto w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center mb-4">
                        <CreditCard className="h-6 w-6 text-indigo-600" />
                    </div>
                    <CardTitle className="text-2xl">Pagos con Stripe</CardTitle>
                    <CardDescription>
                        Paso 3 de 6 — Configura tu cuenta para recibir pagos
                    </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                    {error && (
                        <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                            {error}
                        </div>
                    )}
                    
                    <div className="rounded-lg bg-zinc-50 border border-zinc-200 p-4 text-sm text-zinc-600">
                        <p>
                            Conecta tu cuenta de Stripe para empezar a cobrar a tus clientes. 
                            Puedes hacer esto ahora o más tarde desde la configuración.
                        </p>
                    </div>

                    <Button className="w-full bg-[#635BFF] hover:bg-[#5851E1]" onClick={onConnect} isLoading={isLoading}>
                        Conectar con Stripe
                    </Button>
                </CardContent>

                <CardFooter className="flex justify-between">
                    <Button variant="ghost" onClick={() => router.push("/onboarding/modules")}>
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Atrás
                    </Button>
                    <Button variant="ghost" onClick={onSkip} isLoading={isLoading}>
                        Saltar por ahora
                        <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                </CardFooter>
            </Card>
        </div>
    );
}
