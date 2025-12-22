"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, ArrowRight, Globe } from "lucide-react";

import { apiPost, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

export default function OnboardingDomainPage() {
    const [domain, setDomain] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const onSubmit = async (skip: boolean = false) => {
        setIsLoading(true);
        setError(null);
        try {
            await apiPost("/api/v1/onboarding/domain/", { 
                custom_domain: skip ? "" : domain 
            });
            router.push("/onboarding/invite");
        } catch (err) {
             if (err instanceof ApiError) {
                const body = err.body as Record<string, string[] | string>;
                // Handle different error structures if needed
                setError("Error al guardar dominio");
            } else {
                setError("Error de conexión");
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-zinc-100 px-4 py-12">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <div className="mx-auto w-12 h-12 rounded-xl bg-teal-100 flex items-center justify-center mb-4">
                        <Globe className="h-6 w-6 text-teal-600" />
                    </div>
                    <CardTitle className="text-2xl">Dominio Personalizado</CardTitle>
                    <CardDescription>
                        Paso 4 de 6 — Usa tu propio dominio para tu sitio
                    </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                     {error && (
                        <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                            {error}
                        </div>
                    )}
                    
                    <div className="space-y-2">
                        <p className="text-sm text-zinc-600">
                            Si tienes un dominio (ej. <code>tuempresa.com</code>), puedes configurarlo aquí. 
                            De lo contrario, usaremos tu subdominio gratuito.
                        </p>
                    </div>

                    <Input
                        placeholder="app.tuempresa.com"
                        value={domain}
                        onChange={(e) => setDomain(e.target.value)}
                    />
                </CardContent>

                <CardFooter className="flex justify-between">
                     <Button variant="ghost" onClick={() => router.push("/onboarding/stripe")}>
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Atrás
                    </Button>
                     <div className="flex gap-2">
                        <Button variant="ghost" onClick={() => onSubmit(true)} isLoading={isLoading}>
                            Saltar
                        </Button>
                        <Button onClick={() => onSubmit(false)} disabled={!domain} isLoading={isLoading}>
                            Guardar
                            <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                     </div>
                </CardFooter>
            </Card>
        </div>
    );
}
