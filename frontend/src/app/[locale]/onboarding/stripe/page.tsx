"use client";

import { useState } from "react";
import { useRouter } from "@/lib/navigation";
import { useTranslations } from "next-intl";
import { ArrowLeft, ArrowRight, CreditCard } from "lucide-react";

import { apiPost, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

export default function OnboardingStripePage() {
    const t = useTranslations("onboarding.step3");
    const te = useTranslations("onboarding.errors");
    const tc = useTranslations("common");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const onSkip = async () => {
        setIsLoading(true);
        try {
            await apiPost("/api/v1/onboarding/stripe/", { stripe_connected: false });
            router.push("/onboarding/domain");
        } catch (err) {
            setError(te("stripeError"));
            setIsLoading(false);
        }
    };

    const onConnect = async () => {
        setIsLoading(true);
        try {
            await apiPost("/api/v1/onboarding/stripe/", { stripe_connected: true });
            router.push("/onboarding/domain");
        } catch (err) {
            setError(te("stripeError"));
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-zinc-100 px-4 py-12">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <div className="mx-auto w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center mb-4">
                        <CreditCard className="h-6 w-6 text-indigo-600" />
                    </div>
                    <CardTitle className="text-2xl">{t("title")}</CardTitle>
                    <CardDescription>
                        {t("description")}
                    </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                    {error && (
                        <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                            {error}
                        </div>
                    )}

                    <div className="rounded-lg bg-zinc-50 border border-zinc-200 p-4 text-sm text-zinc-600">
                        <p>
                            {t("connectDescription")}
                        </p>
                    </div>

                    <Button className="w-full bg-[#635BFF] hover:bg-[#5851E1]" onClick={onConnect} isLoading={isLoading}>
                        {t("connect")}
                    </Button>
                </CardContent>

                <CardFooter className="flex justify-between">
                    <Button variant="ghost" onClick={() => router.push("/onboarding/modules")}>
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        {tc("back")}
                    </Button>
                    <Button variant="ghost" onClick={onSkip} isLoading={isLoading}>
                        {t("skipForNow")}
                        <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                </CardFooter>
            </Card>
        </div>
    );
}
