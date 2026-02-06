"use client";

import { Link } from "@/lib/navigation";
import { useTranslations } from "next-intl";
import { CheckCircle2, ArrowRight, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

export default function OnboardingDonePage() {
    const t = useTranslations("onboarding.step6");

    return (
        <div className="min-h-screen flex items-center justify-center bg-background px-4 py-12">
            <Card className="w-full max-w-lg text-center">
                <CardHeader>
                    <div className="mx-auto w-16 h-16 rounded-full bg-green-500/10 flex items-center justify-center mb-4">
                        <CheckCircle2 className="h-8 w-8 text-success-text" />
                    </div>
                    <CardTitle className="text-2xl">{t("title")}</CardTitle>
                    <CardDescription>
                        {t("description")}
                    </CardDescription>
                </CardHeader>

                <CardContent className="space-y-6">
                    <div className="flex items-center gap-3 rounded-lg bg-primary/10 p-4 text-left">
                        <Sparkles className="h-5 w-5 text-primary shrink-0" />
                        <div>
                            <p className="font-medium text-foreground">{t("nextSteps")}</p>
                            <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                                <li>&bull; {t("exploreDashboard")}</li>
                                <li>&bull; {t("configureRoles")}</li>
                                <li>&bull; {t("inviteMore")}</li>
                                <li>&bull; {t("customizePlan")}</li>
                            </ul>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-left">
                        <div className="rounded-lg border border-border p-3">
                            <p className="text-xs font-medium text-muted-foreground">{t("stepCompleted")}</p>
                            <p className="font-medium text-foreground">{t("orgCreated")}</p>
                        </div>
                        <div className="rounded-lg border border-border p-3">
                            <p className="text-xs font-medium text-muted-foreground">{t("stepCompleted")}</p>
                            <p className="font-medium text-foreground">{t("modulesConfigured")}</p>
                        </div>
                        <div className="rounded-lg border border-border p-3">
                            <p className="text-xs font-medium text-muted-foreground">{t("stepCompleted")}</p>
                            <p className="font-medium text-foreground">{t("domainAssigned")}</p>
                        </div>
                        <div className="rounded-lg border border-border p-3">
                            <p className="text-xs font-medium text-muted-foreground">{t("stepCompleted")}</p>
                            <p className="font-medium text-foreground">{t("teamInvited")}</p>
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
                    <p className="text-xs text-muted-foreground">
                        {t("accessSettings")}
                    </p>
                </CardFooter>
            </Card>
        </div>
    );
}
