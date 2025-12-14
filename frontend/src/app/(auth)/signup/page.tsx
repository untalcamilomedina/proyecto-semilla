"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { apiPost, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

const signupSchema = z.object({
    email: z.string().email("Email inválido"),
    password1: z.string().min(8, "Mínimo 8 caracteres"),
    password2: z.string(),
}).refine((data) => data.password1 === data.password2, {
    message: "Las contraseñas no coinciden",
    path: ["password2"],
});

type SignupForm = z.infer<typeof signupSchema>;

export default function SignupPage() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<SignupForm>({
        resolver: zodResolver(signupSchema),
    });

    const onSubmit = async (data: SignupForm) => {
        setIsLoading(true);
        setError(null);

        try {
            await apiPost("/api/v1/signup/", {
                email: data.email,
                password1: data.password1,
                password2: data.password2,
            });
            router.push("/login?registered=true");
        } catch (err) {
            if (err instanceof ApiError) {
                const body = err.body as Record<string, string[]>;
                const firstError = Object.values(body).flat()[0];
                setError(firstError || "Error al registrar");
            } else {
                setError("Error de conexión");
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-zinc-50 px-4">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <CardTitle className="text-2xl">Crear cuenta</CardTitle>
                    <CardDescription>
                        Regístrate para comenzar a usar la plataforma
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
                            label="Email"
                            type="email"
                            placeholder="tu@email.com"
                            error={errors.email?.message}
                            {...register("email")}
                        />

                        <Input
                            label="Contraseña"
                            type="password"
                            placeholder="Mínimo 8 caracteres"
                            error={errors.password1?.message}
                            {...register("password1")}
                        />

                        <Input
                            label="Confirmar contraseña"
                            type="password"
                            placeholder="Repite tu contraseña"
                            error={errors.password2?.message}
                            {...register("password2")}
                        />
                    </CardContent>

                    <CardFooter className="flex flex-col gap-4">
                        <Button type="submit" className="w-full" isLoading={isLoading}>
                            Crear cuenta
                        </Button>

                        <p className="text-sm text-zinc-500 text-center">
                            ¿Ya tienes cuenta?{" "}
                            <Link href="/login" className="text-indigo-600 hover:underline">
                                Iniciar sesión
                            </Link>
                        </p>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
