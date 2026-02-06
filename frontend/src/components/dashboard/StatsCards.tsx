import { GlassCard } from "@/components/ui/glass-card";
import { useTranslations } from "next-intl";
import { Activity, Database, Zap, CreditCard } from "lucide-react";

interface StatsCardsProps {
    usage?: {
        diagrams_used: number;
        max_diagrams: number;
        requests_used: number;
        max_requests: number;
    };
    planName?: string;
    isLoading?: boolean;
}

export function StatsCards({ usage, planName, isLoading }: StatsCardsProps) {
    const t = useTranslations("dashboard.stats");

    if (isLoading) {
        return (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {[...Array(4)].map((_, i) => (
                    <GlassCard key={i} className="h-32 animate-pulse bg-glass-bg" children={null} />
                ))}
            </div>
        );
    }

    const cards = [
        {
            title: t("diagrams" as any) || "Diagrams",
            value: `${usage?.diagrams_used || 0} / ${usage?.max_diagrams || "∞"}`,
            icon: Database,
            color: "text-blue-400",
        },
        {
            title: t("requests" as any) || "API Requests",
            value: `${usage?.requests_used || 0} / ${usage?.max_requests || "∞"}`,
            icon: Zap,
            color: "text-yellow-400",
        },
        {
            title: t("plan" as any) || "Current Plan",
            value: planName || "Free",
            icon: CreditCard,
            color: "text-purple-400",
        },
        {
            title: t("activity" as any) || "Health",
            value: "98%",
            icon: Activity,
            color: "text-green-400",
        },
    ];

    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {cards.map((card, index) => {
                const Icon = card.icon;
                return (
                    <GlassCard key={index} className="flex flex-col justify-between">
                        <div className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <span className="text-sm font-medium text-text-subtle">
                                {card.title}
                            </span>
                            <Icon className={`h-4 w-4 ${card.color}`} />
                        </div>
                        <div className="text-2xl font-bold text-foreground">
                            {card.value}
                        </div>
                    </GlassCard>
                );
            })}
        </div>
    );
}
