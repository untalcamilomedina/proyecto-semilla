"use client";

import { useState } from "react";
import { useRouter, Link } from "@/lib/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useTranslations } from "next-intl";
import { apiPost, ApiError } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { AuthLayout } from "@/components/auth/AuthLayout";

/**
 * LoginPage
 * Provides a premium authentication experience using Glassmorphism.
 *
 * @vibe Elite - Deep blur, neon accents, and full i18n support.
 */
export default function LoginPage() {
  const t = useTranslations("auth");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { checkAuth } = useAuth();

  const loginSchema = z.object({
    email: z
      .string()
      .email(t("validation.invalidEmail" as any) || "Email inválido"),
    password: z
      .string()
      .min(
        1,
        t("validation.passwordRequired" as any) || "La contraseña es requerida",
      ),
  });

  type LoginForm = z.infer<typeof loginSchema>;

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
      await apiPost("/login/", {
        email: data.email,
        password: data.password,
      });
      await checkAuth();
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof ApiError) {
        const body = err.body as {
          detail?: string;
          non_field_errors?: string[];
        };
        setError(
          body?.detail ||
            body?.non_field_errors?.[0] ||
            t("invalidCredentials"),
        );
      } else {
        setError(t("connectionError"));
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout title={t("login")} description={t("loginDescription")}>
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

          <div className="space-y-1">
            <GlassInput
              label={t("password")}
              type="password"
              placeholder={t("passwordPlaceholder")}
              error={errors.password?.message}
              {...register("password")}
            />
            <div className="flex justify-end px-1">
              <Link
                href="/forgot-password"
                className="text-[11px] text-neon-text hover:text-neon-text transition-colors"
              >
                {t("forgotPassword")}
              </Link>
            </div>
          </div>
        </div>

        <div className="pt-2 space-y-6">
          <GlassButton
            type="submit"
            className="w-full h-12 text-base"
            disabled={isLoading}
          >
            {isLoading ? "..." : t("login")}
          </GlassButton>

          <p className="text-sm text-text-tertiary text-center">
            {t("noAccount")}{" "}
            <Link
              href="/signup"
              className="text-neon-text hover:text-neon-text font-medium transition-colors"
            >
              {t("register")}
            </Link>
          </p>
        </div>
      </form>
    </AuthLayout>
  );
}
