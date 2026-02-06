"use client";

// Skip static generation - requires auth
export const dynamic = "force-dynamic";

import { useEffect, useState } from "react";
import { Link } from "@/lib/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/use-auth";
import { GlassCard } from "@/components/ui/glass/GlassCard";
import { Users, Shield, CreditCard, BarChart3, ArrowRight } from "lucide-react";
import { apiGet } from "@/lib/api";
import { cn } from "@/lib/utils";

interface DashboardData {
    stats: {
        total_members: number;
        active_members: number;
        pending_invites: number;
        mrr: number;
    };
    recent_activity: any[];
    modules_status: Record<string, string>;
}

/**
 * DashboardPage
 * The heart of the Elite Experience.
 * 
 * @vibe Enterprise - Data visualization with Glassmorphism and performance focus.
 */
export default function DashboardPage() {
    const t = useTranslations("dashboard");
    const tc = useTranslations("common");
    const { tenant, user } = useAuth();
    const [data, setData] = useState<DashboardData | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await apiGet<DashboardData>("/api/v1/dashboard/");
                setData(response);
            } catch (error) {
                console.error("Error fetching dashboard data:", error);
            } finally {
                setIsLoading(false);
            }
        };

        if (tenant) {
            fetchData();
        }
    }, [tenant]);

    const stats = [
        { 
            name: t("stats.members"), 
            value: isLoading ? "..." : data?.stats.total_members.toString() || "0", 
            icon: Users, 
            color: "text-blue-400",
            bg: "bg-blue-500/10"
        },
        { 
            name: t("stats.roles"), 
            value: "3", 
            icon: Shield, 
            color: "text-neon",
            bg: "bg-neon/10"
        },
        { 
            name: t("stats.billing"), 
            value: isLoading ? "..." : `$${data?.stats.mrr || 0}`, 
            icon: CreditCard, 
            color: "text-purple-400",
            bg: "bg-purple-500/10"
        },
        { 
            name: t("stats.usage"), 
            value: "12%", 
            icon: BarChart3, 
            color: "text-orange-400",
            bg: "bg-orange-500/10"
        },
    ];

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
                        {t("title")}
                    </h1>
                    <p className="mt-1 text-white/40 font-medium">
                        {t("welcome", { name: user?.first_name || user?.username || tc("user") })}
                    </p>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                {stats.map((stat) => (
                    <GlassCard key={stat.name} className="p-6 group hover:translate-y-[-4px] transition-all duration-300">
                        <div className="flex items-center gap-4">
                            <div className={cn(
                                "flex h-12 w-12 items-center justify-center rounded-2xl transition-transform duration-500 group-hover:rotate-12",
                                stat.bg
                            )}>
                                <stat.icon className={cn("h-6 w-6", stat.color)} />
                            </div>
                            <div>
                                <p className="text-xs font-medium text-white/40 mb-0.5">{stat.name}</p>
                                <p className="text-2xl font-bold text-white tracking-tight">{stat.value}</p>
                            </div>
                        </div>
                    </GlassCard>
                ))}
            </div>

            {/* Bottom Section */}
            <div className="grid gap-8 lg:grid-cols-3">
                {/* Organization Info */}
                <GlassCard className="lg:col-span-2 p-8">
                    <div className="flex items-center justify-between mb-8">
                        <h2 className="text-xl font-bold text-white/90">{t("organization")}</h2>
                        <span className="px-3 py-1 rounded-full bg-neon/10 border border-neon/20 text-neon text-[10px] uppercase font-bold tracking-wider">
                            {tenant?.plan_code || t("stats.plan")}
                        </span>
                    </div>
                    
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
                        <div className="space-y-1">
                            <p className="text-xs font-medium text-white/30 uppercase tracking-widest">{t("name")}</p>
                            <p className="text-lg font-semibold text-white/90">{tenant?.name}</p>
                        </div>
                        <div className="space-y-1">
                            <p className="text-xs font-medium text-white/30 uppercase tracking-widest">{t("slug")}</p>
                            <p className="text-sm font-mono text-neon/80">@{tenant?.slug}</p>
                        </div>
                        <div className="space-y-1">
                            <p className="text-xs font-medium text-white/30 uppercase tracking-widest">{t("modules")}</p>
                            <p className="text-lg font-semibold text-white/90">{t("modulesActive", { count: tenant?.enabled_modules?.length || 0 })}</p>
                        </div>
                    </div>
                </GlassCard>

                {/* Quick Actions */}
                <div className="space-y-6">
                    <h2 className="text-xl font-bold text-white/90 px-2">{t("quickActions")}</h2>
                    <div className="grid gap-3">
                        <Link 
                            href="/members" 
                            className="group flex items-center justify-between p-4 rounded-2xl bg-white/[0.03] border border-white/5 hover:bg-white/[0.08] hover:border-white/10 transition-all duration-300"
                        >
                            <div className="flex items-center gap-3">
                                <Users className="h-5 w-5 text-blue-400" />
                                <span className="text-sm font-medium text-white/70 group-hover:text-white">{t("inviteMembers")}</span>
                            </div>
                            <ArrowRight className="h-4 w-4 text-white/20 group-hover:text-neon group-hover:translate-x-1 transition-all" />
                        </Link>
                        
                        <Link 
                            href="/roles" 
                            className="group flex items-center justify-between p-4 rounded-2xl bg-white/[0.03] border border-white/5 hover:bg-white/[0.08] hover:border-white/10 transition-all duration-300"
                        >
                            <div className="flex items-center gap-3">
                                <Shield className="h-5 w-5 text-neon" />
                                <span className="text-sm font-medium text-white/70 group-hover:text-white">{t("manageRoles")}</span>
                            </div>
                            <ArrowRight className="h-4 w-4 text-white/20 group-hover:text-neon group-hover:translate-x-1 transition-all" />
                        </Link>

                        <Link 
                            href="/billing" 
                            className="group flex items-center justify-between p-4 rounded-2xl bg-white/[0.03] border border-white/5 hover:bg-white/[0.08] hover:border-white/10 transition-all duration-300"
                        >
                            <div className="flex items-center gap-3">
                                <CreditCard className="h-5 w-5 text-purple-400" />
                                <span className="text-sm font-medium text-white/70 group-hover:text-white">{t("viewBilling")}</span>
                            </div>
                            <ArrowRight className="h-4 w-4 text-white/20 group-hover:text-neon group-hover:translate-x-1 transition-all" />
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
