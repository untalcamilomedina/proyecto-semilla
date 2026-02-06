"use client";

import { Link } from "@/lib/navigation";
import { useTranslations } from "next-intl";
import { CheckCircle2, ArrowRight, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

export default function OnboardingDonePage() {
    const t = useTranslations("onboarding.step6");

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-zinc-100 px-4 py-12">
            <Card className="w-full max-w-lg text-center">
                <CardHeader>
                    <div className="mx-auto w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mb-4">
                        <CheckCircle2 className="h-8 w-8 text-green-600" />
                    </div>
                    <CardTitle className="text-2xl">{t("title")}</CardTitle>
                    <CardDescription>
                        {t("description")}
                    </CardDescription>
                </CardHeader>

                <CardContent className="space-y-6">
                    <div className="flex items-center gap-3 rounded-lg bg-indigo-50 p-4 text-left">
                        <Sparkles className="h-5 w-5 text-indigo-500 shrink-0" />
                        <div>
                            <p className="font-medium text-indigo-900">{t("nextSteps")}</p>
                            <ul className="mt-2 space-y-1 text-sm text-indigo-700">
                                <li>&bull; {t("exploreDashboard")}</li>
                                <li>&bull; {t("configureRoles")}</li>
                                <li>&bull; {t("inviteMore")}</li>
                                <li>&bull; {t("customizePlan")}</li>
                            </ul>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-left">
                        <div className="rounded-lg border border-zinc-200 p-3">
                            <p className="text-xs font-medium text-zinc-500">{t("stepCompleted")}</p>
                            <p className="font-medium text-zinc-900">{t("orgCreated")}</p>
                        </div>
                        <div className="rounded-lg border border-zinc-200 p-3">
                            <p className="text-xs font-medium text-zinc-500">{t("stepCompleted")}</p>
                            <p className="font-medium text-zinc-900">{t("modulesConfigured")}</p>
                        </div>
                        <div className="rounded-lg border border-zinc-200 p-3">
                            <p className="text-xs font-medium text-zinc-500">{t("stepCompleted")}</p>
                            <p className="font-medium text-zinc-900">{t("domainAssigned")}</p>
                        </div>
                        <div className="rounded-lg border border-zinc-200 p-3">
                            <p className="text-xs font-medium text-zinc-500">{t("stepCompleted")}</p>
                            <p className="font-medium text-zinc-900">{t("teamInvited")}</p>
                        </div>
                    </div>
                </CardContent>

                <CardFooter className="flex-col gap-3">
                    <Button asChild className="w-full">
                        <Link href="/">
                            {t("goToDashboard")}
                            <ArrowRight className="ml-2 h-4 w-4" />
                        </Link>
                    </Button>
                    <p className="text-xs text-zinc-500">
                        {t("accessSettings")}
                    </p>
                </CardFooter>
            </Card>
        </div>
    );
}
