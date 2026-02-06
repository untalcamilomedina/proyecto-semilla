"use client";

import { Member } from "@/types/member";
import { useTranslations } from "next-intl";
import { DataTable } from "./data-table";
import { getColumns } from "./columns";
import { useAuth } from "@/hooks/use-auth";
import { useResourceQuery } from "@/hooks/use-api";
import { GlassCard } from "@/components/ui/glass/GlassCard";
import { TableSkeleton } from "@/components/ui/table-skeleton";

/**
 * MembersTable
 * Specialized component for rendering the members list with Glassmorphism.
 */
export function MembersTable() {
    const t = useTranslations("members");
    const { tenant } = useAuth();
    const columns = getColumns(t);

    const { data, isLoading } = useResourceQuery<Member[]>(
        ["members"],
        "/api/v1/memberships/",
        { enabled: !!tenant }
    );

    if (isLoading) {
        return (
            <GlassCard className="border-glass-border-subtle">
                <TableSkeleton rows={5} columns={4} />
            </GlassCard>
        );
    }

    return (
        <GlassCard className="p-0 overflow-hidden border-glass-border-subtle bg-glass-bg">
            <div className="p-4 md:p-6">
                <DataTable columns={columns} data={data ?? []} />
            </div>
        </GlassCard>
    );
}
