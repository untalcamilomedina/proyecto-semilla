"use client";

import { useState } from "react";
import { useRouter } from "@/lib/navigation";
import { useTranslations } from "next-intl";
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
    const t = useTranslations("onboarding.step5");
    const te = useTranslations("onboarding.errors");
    const tc = useTranslations("common");
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

            await apiPost("/onboarding/invite/", { emails });
            router.push("/onboarding/done");
        } catch (err) {
            if (err instanceof ApiError) {
                setError(te("inviteError"));
            } else {
                setError(te("connectionError"));
            }
        } finally {
            setIsLoading(false);
        }
    };

    const onSkip = async () => {
        setIsLoading(true);
        setError(null);
        try {
            await apiPost("/onboarding/invite/", { emails: [] });
            router.push("/onboarding/done");
        } catch (err) {
            router.push("/onboarding/done");
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-background px-4 py-12">
            <Card className="w-full max-w-lg">
                <CardHeader className="text-center">
                    <div className="mx-auto w-12 h-12 rounded-xl bg-orange-500/10 flex items-center justify-center mb-4">
                        <Users className="h-6 w-6 text-orange-400" />
                    </div>
                    <CardTitle className="text-2xl">{t("title")}</CardTitle>
                    <CardDescription>
                        {t("description")}
                    </CardDescription>
                </CardHeader>

                <form onSubmit={handleSubmit(onSubmit)}>
                    <CardContent className="space-y-4">
                        {error && (
                            <div className="rounded-md bg-error-bg border border-error-border p-3 text-sm text-error-text">
                                {error}
                            </div>
                        )}

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-foreground">
                                {t("memberEmails")}
                            </label>
                            <textarea
                                rows={5}
                                className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                placeholder={t("emailsPlaceholder")}
                                {...register("emails")}
                            />
                            <p className="text-xs text-muted-foreground">
                                {t("emailsHint")}
                            </p>
                        </div>

                        <div className="flex items-center gap-3 rounded-lg bg-blue-500/10 p-3">
                            <Mail className="h-5 w-5 text-blue-400 shrink-0" />
                            <p className="text-sm text-blue-400">
                                {t("invitationNotice")}
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
                            {tc("back")}
                        </Button>
                        <Button
                            type="button"
                            variant="ghost"
                            onClick={onSkip}
                            disabled={isLoading}
                        >
                            {t("skipForNow")}
                        </Button>
                        <Button type="submit" className="flex-1" isLoading={isLoading}>
                            {isLoading ? t("sending") : t("sendInvitations")}
                            <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
