"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { ArrowRight, ArrowLeft, Users, Mail } from "lucide-react";

import { apiPost, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

const inviteSchema = z.object({
    emails: z.string().optional(),
});

type InviteForm = z.infer<typeof inviteSchema>;

export default function OnboardingInvitePage() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const { register, handleSubmit } = useForm<InviteForm>({
        resolver: zodResolver(inviteSchema),
    });

    const onSubmit = async (data: InviteForm) => {
        setIsLoading(true);
        setError(null);

        try {
            const emails = (data.emails || "")
                .split(/[\n,]/)
                .map((e) => e.trim().toLowerCase())
                .filter((e) => e.includes("@"));

            await apiPost("/api/v1/onboarding/invite/", { emails });
            router.push("/onboarding/done");
        } catch (err) {
            if (err instanceof ApiError) {
                setError("Error al enviar invitaciones");
            } else {
                setError("Error de conexión");
            }
        } finally {
            setIsLoading(false);
        }
    };

    const onSkip = async () => {
        setIsLoading(true);
        setError(null);
        try {
            // Send empty list to mark step as completed without invites
            await apiPost("/api/v1/onboarding/invite/", { emails: [] });
            router.push("/onboarding/done");
        } catch (err) {
            // Even if API fails, we can probably proceed to done in this specific skipping case
            // But let's try to be consistent
            router.push("/onboarding/done");
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-zinc-100 px-4 py-12">
            <Card className="w-full max-w-lg">
                <CardHeader className="text-center">
                    <div className="mx-auto w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center mb-4">
                        <Users className="h-6 w-6 text-orange-600" />
                    </div>
                    <CardTitle className="text-2xl">Invita a tu equipo</CardTitle>
                    <CardDescription>
                        Paso 5 de 6 — Agrega miembros a tu organización
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
                                Emails de los miembros
                            </label>
                            <textarea
                                rows={5}
                                className="flex w-full rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                                placeholder="email1@ejemplo.com&#10;email2@ejemplo.com&#10;email3@ejemplo.com"
                                {...register("emails")}
                            />
                            <p className="text-xs text-zinc-500">
                                Un email por línea o separados por comas
                            </p>
                        </div>

                        <div className="flex items-center gap-3 rounded-lg bg-blue-50 p-3">
                            <Mail className="h-5 w-5 text-blue-500 shrink-0" />
                            <p className="text-sm text-blue-700">
                                Se enviará un email de invitación a cada dirección
                            </p>
                        </div>
                    </CardContent>

                    <CardFooter className="flex gap-3">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => router.push("/onboarding/domain")}
                        >
                            <ArrowLeft className="mr-2 h-4 w-4" />
                            Atrás
                        </Button>
                        <Button 
                            type="button" 
                            variant="ghost" 
                            onClick={onSkip} 
                            disabled={isLoading}
                        >
                            Saltar
                        </Button>
                        <Button type="submit" className="flex-1" isLoading={isLoading}>
                            {isLoading ? "Enviando..." : "Enviar invitaciones"}
                            <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
