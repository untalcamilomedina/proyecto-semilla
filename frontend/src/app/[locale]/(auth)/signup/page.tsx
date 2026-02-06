"use client";

import { useState } from "react";
import { useRouter, Link } from "@/lib/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useTranslations } from "next-intl";
import { apiPost, ApiError } from "@/lib/api";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { AuthLayout } from "@/components/auth/AuthLayout";

/**
 * SignupPage
 * Provides a premium registration experience using Glassmorphism.
 * 
 * @vibe Elite - Cyber-Premium aesthetic with neon glow and full i18n.
 */
export default function SignupPage() {
    const t = useTranslations("auth");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const signupSchema = z.object({
        email: z.string().email(t("validation.invalidEmail" as any) || "Email inválido"),
        password1: z.string().min(8, t("validation.minChars" as any, { count: 8 }) || "Mínimo 8 caracteres"),
        password2: z.string(),
    }).refine((data) => data.password1 === data.password2, {
        message: t("validation.passwordsMatch" as any) || "Las contraseñas no coinciden",
        path: ["password2"],
    });

    type SignupForm = z.infer<typeof signupSchema>;

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
                setError(firstError || t("errors.startError" as any) || "Error al registrar");
            } else {
                setError(t("connectionError"));
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <AuthLayout 
            title={t("signup")} 
            description={t("signupDescription")}
        >
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                {error && (
                    <div className="rounded-xl bg-red-500/10 border border-red-500/20 p-4 text-sm text-red-400 animate-in fade-in slide-in-from-top-1 duration-300">
                        {error}
                    </div>
                )}

                <div className="space-y-4">
                    <GlassInput
                        label={t("email")}
                        type="email"
                        placeholder={t("emailPlaceholder")}
                        error={errors.email?.message}
                        {...register("email")}
                    />

                    <GlassInput
                        label={t("password")}
                        type="password"
                        placeholder={t("signupPasswordPlaceholder")}
                        error={errors.password1?.message}
                        {...register("password1")}
                    />

                    <GlassInput
                        label={t("confirmPassword")}
                        type="password"
                        placeholder={t("confirmPasswordPlaceholder")}
                        error={errors.password2?.message}
                        {...register("password2")}
                    />
                </div>

                <div className="pt-2 space-y-6">
                    <GlassButton 
                        type="submit" 
                        className="w-full h-12 text-base" 
                        disabled={isLoading}
                    >
                        {isLoading ? "..." : t("createAccount")}
                    </GlassButton>

                    <p className="text-sm text-white/40 text-center">
                        {t("haveAccount")}{" "}
                        <Link href="/login" className="text-neon hover:text-neon/80 font-medium transition-colors">
                            {t("login")}
                        </Link>
                    </p>
                </div>
            </form>
        </AuthLayout>
    );
}
