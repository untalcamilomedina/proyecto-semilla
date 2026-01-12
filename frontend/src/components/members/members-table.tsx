"use client";

import { useEffect, useState } from "react";
import { Member } from "@/types/member";
import { memberService } from "@/services/members";
import { DataTable } from "./data-table";
import { columns } from "./columns";
import { useAuth } from "@/hooks/use-auth";
import { GlassCard } from "@/components/ui/glass/GlassCard";

/**
 * MembersTable
 * Specialized component for rendering the members list with Glassmorphism.
 */
export function MembersTable() {
    const t = useTranslations("members");
    const { tenant } = useAuth();
    const [data, setData] = useState<Member[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const columns = getColumns(t);

    useEffect(() => {
        const fetchMembers = async () => {
            try {
                const members = await memberService.getAll();
                setData(members);
            } catch (error) {
                console.error("Failed to fetch members:", error);
            } finally {
                setIsLoading(false);
            }
        };

        if (tenant) {
            fetchMembers();
        }
    }, [tenant]);

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
