"use client";

import { useState } from "react";
import { Link } from "@/lib/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useTranslations } from "next-intl";
import { apiPost, ApiError } from "@/lib/api";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { AuthLayout } from "@/components/auth/AuthLayout";

/**
 * ForgotPasswordPage
 * Allows users to request a password reset link.
 */
export default function ForgotPasswordPage() {
    const t = useTranslations("auth");
    const [isLoading, setIsLoading] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const resetSchema = z.object({
        email: z.string().email(t("validation.invalidEmail" as any) || "Email inválido"),
    });

    type ResetForm = z.infer<typeof resetSchema>;

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<ResetForm>({
        resolver: zodResolver(resetSchema),
    });

    const onSubmit = async (data: ResetForm) => {
        setIsLoading(true);
        setError(null);

        try {
            await apiPost("/api/v1/password/reset/", {
                email: data.email,
            });
            setIsSuccess(true);
        } catch (err) {
             // We generally don't want to confirm/deny email existence for security,
             // but if API returns specific error we show it or generic error.
             // For this UI, we treat success to prevent enumeration if API supports it.
            if (err instanceof ApiError) {
                 // Log error but maybe still show success or generic error
                 console.error(err);
                 setError(t("connectionError"));
            } else {
                 setError(t("connectionError"));
            }
        } finally {
            setIsLoading(false);
        }
    };

    if (isSuccess) {
         return (
            <AuthLayout 
                title={t("resetTitle")}
                description={t("emailSent")}
            >
                <div className="pt-4">
                     <Link href="/login" className="block w-full">
                        <GlassButton className="w-full">
                            {t("backToLogin")}
                        </GlassButton>
                    </Link>
                </div>
            </AuthLayout>
         );
    }

    return (
        <AuthLayout 
            title={t("resetTitle")} 
            description={t("resetDescription")}
        >
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                {error && (
                    <div className="rounded-xl bg-error-bg border border-error-border p-4 text-sm text-error-text animate-in fade-in slide-in-from-top-1 duration-300">
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
                </div>

                <div className="pt-2 space-y-6">
                    <GlassButton 
                        type="submit" 
                        className="w-full h-12 text-base" 
                        disabled={isLoading}
                    >
                        {isLoading ? "..." : t("sendResetLink")}
                    </GlassButton>

                    <div className="text-center">
                        <Link 
                            href="/login" 
                            className="text-sm text-text-tertiary hover:text-foreground transition-colors"
                        >
                            {t("backToLogin")}
                        </Link>
                    </div>
                </div>
            </form>
        </AuthLayout>
    );
}
