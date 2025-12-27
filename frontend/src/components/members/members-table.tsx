"use client";

import { useEffect, useState } from "react";
import { Member } from "@/types/member";
import { memberService } from "@/services/members";
import { DataTable } from "./data-table";
import { columns } from "./columns";
import { useAuth } from "@/hooks/use-auth";

export function MembersTable() {
    const { tenant } = useAuth();
    const [data, setData] = useState<Member[]>([]);
    const [isLoading, setIsLoading] = useState(true);

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
            <div className="flex items-center justify-center h-64 border rounded-md bg-white">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
            </div>
        );
    }

    return (
        <div className="bg-white rounded-md shadow-sm border border-zinc-200">
            <div className="p-4">
                <DataTable columns={columns} data={data} />
            </div>
        </div>
    );
}
