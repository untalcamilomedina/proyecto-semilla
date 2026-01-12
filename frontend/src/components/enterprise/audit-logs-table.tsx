"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { enterpriseService } from "@/services/enterprise";
import { ActivityLog } from "@/types";
import { GlassCard } from "@/components/ui/glass/GlassCard";
import { DataTable } from "@/components/members/data-table"; // Reuse the generic DataTable if possible
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Clock } from "lucide-react";

export function AuditLogsTable() {
    const t = useTranslations("audit");
    const [data, setData] = useState<ActivityLog[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const response = await enterpriseService.getAuditLogs();
                setData(response.results);
            } catch (error) {
                console.error("Failed to fetch audit logs:", error);
            } finally {
                setIsLoading(false);
            }
        };
        fetchLogs();
    }, []);

    const columns: ColumnDef<ActivityLog>[] = [
        {
            accessorKey: "actor",
            header: t("actor"),
            cell: ({ row }) => {
                const actor = row.original.actor;
                const email = actor.email;
                const initial = email.charAt(0).toUpperCase();

                return (
                    <div className="flex items-center gap-3">
                        <Avatar className="h-8 w-8 border border-white/10">
                            <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${email}`} />
                            <AvatarFallback className="bg-neon/10 text-neon text-[10px]">{initial}</AvatarFallback>
                        </Avatar>
                        <div className="flex flex-col">
                            <span className="text-xs font-semibold text-white/90">{email.split("@")[0]}</span>
                            <span className="text-[9px] text-white/30 font-mono">{email}</span>
                        </div>
                    </div>
                );
            },
        },
        {
            accessorKey: "action",
            header: t("action"),
            cell: ({ row }) => {
                const action = row.original.action;
                return (
                    <Badge className="bg-white/5 text-white/60 border-white/10 text-[10px] uppercase tracking-wider font-bold">
                        {action}
                    </Badge>
                );
            },
        },
        {
            accessorKey: "target",
            header: t("target"),
            cell: ({ row }) => (
                <span className="text-xs text-blue-400/80 font-mono">{row.original.target}</span>
            ),
        },
        {
            accessorKey: "created_at",
            header: t("date"),
            cell: ({ row }) => {
                const date = new Date(row.original.created_at);
                return (
                    <div className="flex items-center gap-2 text-white/40 font-mono text-[10px]">
                        <Clock className="h-3 w-3" />
                        {date.toLocaleString()}
                    </div>
                );
            },
        },
    ];

    if (isLoading) {
        return (
            <GlassCard className="flex items-center justify-center h-64 border-white/5">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-neon" />
            </GlassCard>
        );
    }

    return (
        <GlassCard className="p-0 overflow-hidden border-white/5 bg-white/[0.02]">
            <div className="p-4 md:p-6">
                <DataTable columns={columns} data={data} />
            </div>
        </GlassCard>
    );
}
