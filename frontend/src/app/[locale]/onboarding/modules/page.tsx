"use client";

import { useState } from "react";
import { useRouter } from "@/lib/navigation";
import { useTranslations } from "next-intl";
import { ArrowRight, ArrowLeft, Blocks } from "lucide-react";

import { apiPost, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

const MODULE_IDS = ["cms", "lms", "community", "mcp"] as const;

export default function OnboardingModulesPage() {
    const t = useTranslations("onboarding.step2");
    const te = useTranslations("onboarding.errors");
    const tc = useTranslations("common");
    const [selected, setSelected] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const toggleModule = (id: string) => {
        setSelected((prev) =>
            prev.includes(id) ? prev.filter((m) => m !== id) : [...prev, id]
        );
    };

    const onContinue = async () => {
        setIsLoading(true);
        setError(null);

        try {
            await apiPost("/api/v1/onboarding/modules/", { modules: selected });
            router.push("/onboarding/stripe");
        } catch (err) {
            if (err instanceof ApiError) {
                setError(te("modulesError"));
            } else {
                setError(te("connectionError"));
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-background px-4 py-12">
            <Card className="w-full max-w-lg">
                <CardHeader className="text-center">
                    <div className="mx-auto w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-4">
                        <Blocks className="h-6 w-6 text-purple-400" />
                    </div>
                    <CardTitle className="text-2xl">{t("title")}</CardTitle>
                    <CardDescription>
                        {t("description")}
                    </CardDescription>
                </CardHeader>

                <CardContent className="space-y-3">
                    {error && (
                        <div className="rounded-md bg-error-bg border border-error-border p-3 text-sm text-error-text">
                            {error}
                        </div>
                    )}

                    {MODULE_IDS.map((modId) => (
                        <label
                            key={modId}
                            className={`flex items-center gap-3 p-4 rounded-lg border-2 cursor-pointer transition-colors ${selected.includes(modId)
                                    ? "border-primary bg-primary/10"
                                    : "border-border hover:border-ring"
                                }`}
                        >
                            <input
                                type="checkbox"
                                checked={selected.includes(modId)}
                                onChange={() => toggleModule(modId)}
                                className="h-4 w-4 rounded border-input text-primary focus:ring-primary"
                            />
                            <div>
                                <p className="font-medium text-foreground">{t(`modules.${modId}.label`)}</p>
                                <p className="text-sm text-muted-foreground">{t(`modules.${modId}.description`)}</p>
                            </div>
                        </label>
                    ))}

                    <p className="text-xs text-muted-foreground text-center pt-2">
                        {t("changeLater")}
                    </p>
                </CardContent>

                <CardFooter className="flex gap-3">
                    <Button variant="outline" onClick={() => router.push("/onboarding")}>
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        {tc("back")}
                    </Button>
                    <Button className="flex-1" onClick={onContinue} isLoading={isLoading}>
                        {tc("continue")}
                        <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                </CardFooter>
            </Card>
        </div>
    );
}
