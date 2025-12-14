"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { ArrowRight, ArrowLeft, Globe } from "lucide-react";

import { apiPost, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

const domainSchema = z.object({
    custom_domain: z
        .string()
        .optional()
        .refine(
            (val) => !val || /^[a-z0-9]+([\-.][a-z0-9]+)*\.[a-z]{2,}$/.test(val),
            "Dominio inválido (ej: app.ejemplo.com)"
        ),
});

type DomainForm = z.infer<typeof domainSchema>;

export default function OnboardingDomainPage() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<DomainForm>({
        resolver: zodResolver(domainSchema),
    });

    const onSubmit = async (data: DomainForm) => {
        setIsLoading(true);
        setError(null);

        try {
            await apiPost("/api/v1/onboarding/domain/", {
                custom_domain: data.custom_domain || null,
            });
            router.push("/onboarding/invite");
        } catch (err) {
            if (err instanceof ApiError) {
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
            <Card className="w-full max-w-lg">
                <CardHeader className="text-center">
                    <div className="mx-auto w-12 h-12 rounded-xl bg-cyan-100 flex items-center justify-center mb-4">
                        <Globe className="h-6 w-6 text-cyan-600" />
                    </div>
                    <CardTitle className="text-2xl">Dominio personalizado</CardTitle>
                    <CardDescription>
                        Paso 4 de 6 — Opcional: usa tu propio dominio
                    </CardDescription>
                </CardHeader>

                <form onSubmit={handleSubmit(onSubmit)}>
                    <CardContent className="space-y-4">
                        {error && (
                            <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                                {error}
                            </div>
                        )}

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-zinc-700">
                                Dominio personalizado (opcional)
                            </label>
                            <input
                                type="text"
                                className="flex h-10 w-full rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                                placeholder="app.tudominio.com"
                                {...register("custom_domain")}
                            />
                            {errors.custom_domain && (
                                <p className="text-sm text-red-600">
                                    {errors.custom_domain.message}
                                </p>
                            )}
                        </div>

                        <div className="rounded-lg bg-zinc-50 p-4 text-sm text-zinc-600">
                            <p className="font-medium mb-2">Configuración DNS</p>
                            <p>
                                Si configuras un dominio personalizado, deberás agregar un
                                registro CNAME apuntando a <code className="text-xs bg-zinc-200 px-1 py-0.5 rounded">proxy.acme.dev</code>
                            </p>
                        </div>

                        <p className="text-xs text-zinc-500 text-center">
                            Puedes dejar esto vacío y usar el subdominio asignado
                        </p>
                    </CardContent>

                    <CardFooter className="flex gap-3">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => router.push("/onboarding/stripe")}
                        >
                            <ArrowLeft className="mr-2 h-4 w-4" />
                            Atrás
                        </Button>
                        <Button type="submit" className="flex-1" isLoading={isLoading}>
                            Continuar
                            <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
