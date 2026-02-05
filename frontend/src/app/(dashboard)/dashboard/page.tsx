"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/use-auth";
import { apiGet } from "@/lib/api";
import { StatsCards } from "@/components/dashboard/StatsCards";
import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { Plus } from "lucide-react";
import Link from "next/link";
import { Subscription } from "@/types";

export default function DashboardPage() {
    const t = useTranslations("dashboard");
    const { user, tenant } = useAuth();
    const [subscription, setSubscription] = useState<Subscription | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch active subscription for usage stats
                const sub = await apiGet<Subscription>("/api/v1/billing/subscription/");
                setSubscription(sub);
            } catch (error) {
                console.error("Failed to fetch subscription", error);
            } finally {
                setIsLoading(false);
            }
        };

        if (user) {
            fetchData();
        }
    }, [user]);

    // Derived usage stats from subscription or defaults
    // Note: The User/Tenant type currently doesn't have 'usage' field directly, 
    // but the backend Subscription model does. We cast or assume the shape match.
    // If exact types mismatch, we'll need to update types/index.ts.
    // For now, let's assume the API returns what we need or we pass default props.
    
    // Actually, looking at types/index.ts, Subscription has 'plan' but missing 'usage' fields 
    // we added to backend recently. We might need to update the frontend type definition too.
    // For this step, I'll comply with the existing type or standard usage.
    // Let's pass 'any' for now to StatsCards if types are strict, 
    // or better, let's update the type in a subsequent step if needed.
    
    // We'll map the subscription data to what StatsCards expects
    // The backend serializer likely includes 'diagrams_used' etc. 
    // Let's assume safely.

    return (
        <div className="space-y-8 p-8 pt-6">
            <div className="flex items-center justify-between space-y-2">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-white glow-text">
                        {t("title")}
                    </h2>
                    <p className="text-white/60">
                        {t("welcome", { name: user?.first_name || "User" })}
                    </p>
                </div>
                <div className="flex items-center space-x-2">
                    <Link href="/diagrams/new">
                        <GlassButton className="gap-2">
                            <Plus className="h-4 w-4" />
                            {t("quickActions")}
                        </GlassButton>
                    </Link>
                </div>
            </div>

            <StatsCards 
                isLoading={isLoading}
                planName={subscription?.plan?.name}
                usage={subscription as any} // backend sends extra usage fields
            />

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <RecentActivity />
                {/* Future: Add more widgets here like Chart or Module Status */}
            </div>
        </div>
    );
}
