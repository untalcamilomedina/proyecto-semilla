"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { apiPost, ApiError } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

const loginSchema = z.object({
    email: z.string().email("Email inválido"),
    password: z.string().min(1, "La contraseña es requerida"),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();
    const { checkAuth } = useAuth();

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginForm>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data: LoginForm) => {
        setIsLoading(true);
        setError(null);

        try {
            await apiPost("/api/v1/login/", {
                email: data.email,
                password: data.password,
            });
            await checkAuth();
            router.push("/");
        } catch (err) {
            if (err instanceof ApiError) {
                const body = err.body as { detail?: string; non_field_errors?: string[] };
                setError(
                    body?.detail ||
                    body?.non_field_errors?.[0] ||
                    "Credenciales inválidas"
                );
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
                    <CardTitle className="text-2xl">Iniciar sesión</CardTitle>
                    <CardDescription>
                        Ingresa tus credenciales para acceder al sistema
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
                            placeholder="••••••••"
                            error={errors.password?.message}
                            {...register("password")}
                        />
                    </CardContent>

                    <CardFooter className="flex flex-col gap-4">
                        <Button type="submit" className="w-full" isLoading={isLoading}>
                            Iniciar sesión
                        </Button>

                        <p className="text-sm text-zinc-500 text-center">
                            ¿No tienes cuenta?{" "}
                            <Link href="/signup" className="text-indigo-600 hover:underline">
                                Registrarse
                            </Link>
                        </p>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
