"use client";

import { useTranslations } from "next-intl";
import { AuditLogsTable } from "@/components/enterprise/audit-logs-table";
import { ScrollText } from "lucide-react";

/**
 * AuditLogsPage
 * Enterprise-grade activity monitoring with Glassmorphism Elite.
 * 
 * @vibe Elite - High-integrity audit trail with premium aesthetics.
 */
export default function AuditLogsPage() {
    const t = useTranslations("audit");

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20">
                        <ScrollText className="h-6 w-6 text-blue-400" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white/90">{t("title")}</h1>
                        <p className="text-sm text-white/40">
                            {t("description")}
                        </p>
                    </div>
                </div>
            </div>

            <div className="relative">
                {/* Decorative glow */}
                <div className="absolute -top-40 -left-40 w-80 h-80 bg-blue-500/5 rounded-full blur-[100px] pointer-events-none" />
                
                <AuditLogsTable />
            </div>
        </div>
    );
}
