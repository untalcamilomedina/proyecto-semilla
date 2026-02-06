"use client";

import { useState } from "react";
import { useRouter } from "@/lib/navigation";
import { useTranslations } from "next-intl";
import { ArrowLeft, ArrowRight, Globe } from "lucide-react";

import { apiPost, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

export default function OnboardingDomainPage() {
    const t = useTranslations("onboarding.step4");
    const te = useTranslations("onboarding.errors");
    const tc = useTranslations("common");
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
                setError(te("domainError"));
            } else {
                setError(te("connectionError"));
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-background px-4 py-12">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <div className="mx-auto w-12 h-12 rounded-xl bg-teal-500/10 flex items-center justify-center mb-4">
                        <Globe className="h-6 w-6 text-teal-400" />
                    </div>
                    <CardTitle className="text-2xl">{t("title")}</CardTitle>
                    <CardDescription>
                        {t("description")}
                    </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                     {error && (
                        <div className="rounded-md bg-error-bg border border-error-border p-3 text-sm text-error-text">
                            {error}
                        </div>
                    )}

                    <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                            {t("leaveEmpty")}
                        </p>
                    </div>

                    <Input
                        placeholder={t("customDomainPlaceholder")}
                        value={domain}
                        onChange={(e) => setDomain(e.target.value)}
                    />
                </CardContent>

                <CardFooter className="flex justify-between">
                     <Button variant="ghost" onClick={() => router.push("/onboarding/stripe")}>
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        {tc("back")}
                    </Button>
                     <div className="flex gap-2">
                        <Button variant="ghost" onClick={() => onSubmit(true)} isLoading={isLoading}>
                            {t("skipForNow")}
                        </Button>
                        <Button onClick={() => onSubmit(false)} disabled={!domain} isLoading={isLoading}>
                            {tc("save")}
                            <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                     </div>
                </CardFooter>
            </Card>
        </div>
    );
}
