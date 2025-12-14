"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { ArrowRight, Building2 } from "lucide-react";

import { apiPost, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

const startSchema = z.object({
    org_name: z.string().min(2, "Mínimo 2 caracteres"),
    subdomain: z
        .string()
        .min(3, "Mínimo 3 caracteres")
        .max(30, "Máximo 30 caracteres")
        .regex(/^[a-z0-9-]+$/, "Solo letras minúsculas, números y guiones"),
    admin_email: z.string().email("Email inválido"),
    password: z.string().min(8, "Mínimo 8 caracteres"),
    password_confirm: z.string(),
}).refine((data) => data.password === data.password_confirm, {
    message: "Las contraseñas no coinciden",
    path: ["password_confirm"],
});

type StartForm = z.infer<typeof startSchema>;

export default function OnboardingStartPage() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<StartForm>({
        resolver: zodResolver(startSchema),
    });

    const onSubmit = async (data: StartForm) => {
        setIsLoading(true);
        setError(null);

        try {
            await apiPost("/api/v1/onboarding/start/", {
                org_name: data.org_name,
                subdomain: data.subdomain,
                admin_email: data.admin_email,
                password: data.password,
            });
            router.push("/onboarding/modules");
        } catch (err) {
            if (err instanceof ApiError) {
                const body = err.body as Record<string, string[] | string>;
                const firstError = Object.values(body).flat()[0];
                setError(typeof firstError === "string" ? firstError : "Error al iniciar");
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
                    <div className="mx-auto w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center mb-4">
                        <Building2 className="h-6 w-6 text-indigo-600" />
                    </div>
                    <CardTitle className="text-2xl">Crea tu organización</CardTitle>
                    <CardDescription>
                        Paso 1 de 6 — Configura tu espacio de trabajo
                    </CardDescription>
                </CardHeader>

                <form onSubmit={handleSubmit(onSubmit)}>
                    <CardContent className="space-y-4">
                        {error && (
                            <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                                {error}
                            </div>
                        )}

                        <Input
                            label="Nombre de la organización"
                            placeholder="Mi Empresa"
                            error={errors.org_name?.message}
                            {...register("org_name")}
                        />

                        <div className="space-y-1.5">
                            <label className="text-sm font-medium text-zinc-700">
                                Subdominio
                            </label>
                            <div className="flex">
                                <input
                                    type="text"
                                    className="flex h-9 w-full rounded-l-md border border-r-0 border-zinc-200 bg-white px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                                    placeholder="mi-empresa"
                                    {...register("subdomain")}
                                />
                                <span className="inline-flex items-center rounded-r-md border border-zinc-200 bg-zinc-50 px-3 text-sm text-zinc-500">
                                    .acme.dev
                                </span>
                            </div>
                            {errors.subdomain && (
                                <p className="text-sm text-red-600">{errors.subdomain.message}</p>
                            )}
                        </div>

                        <Input
                            label="Email del administrador"
                            type="email"
                            placeholder="admin@ejemplo.com"
                            error={errors.admin_email?.message}
                            {...register("admin_email")}
                        />

                        <Input
                            label="Contraseña"
                            type="password"
                            placeholder="Mínimo 8 caracteres"
                            error={errors.password?.message}
                            {...register("password")}
                        />

                        <Input
                            label="Confirmar contraseña"
                            type="password"
                            placeholder="Repite tu contraseña"
                            error={errors.password_confirm?.message}
                            {...register("password_confirm")}
                        />
                    </CardContent>

                    <CardFooter>
                        <Button type="submit" className="w-full" isLoading={isLoading}>
                            Continuar
                            <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
