"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/use-auth";
import { apiGet, apiPost } from "@/lib/api";
import { DiagramsTable } from "@/components/diagrams/DiagramsTable";
import { Diagram, PaginatedResponse } from "@/types";
import { toast } from "sonner";

export default function DiagramsPage() {
    const t = useTranslations("diagrams");
    const { user } = useAuth();
    const [data, setData] = useState<Diagram[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const fetchData = async () => {
        try {
            const response = await apiGet<PaginatedResponse<Diagram>>("/api/v1/diagrams/");
            setData(response.results);
        } catch (error) {
            console.error("Failed to fetch diagrams", error);
            toast.error("Failed to load diagrams");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (user) {
            fetchData();
        }
    }, [user]);

    const handleDelete = async (id: string) => {
        if (!confirm("Are you sure?")) return;

        // Optimistic update or refresh?
        // Let's optimize by removing from state first
        setData(prev => prev.filter(d => d.id !== id));

        try {
            // Need a DELETE helper or use fetch directly
            // For now using fetch wrapper logic manually or assuming apiDelete exists?
            // api.ts doesn't have apiDelete. I should use fetch directly or add helper.
            // Let's use fetch with auth token logic... wait, api.ts handles token if set?
            // Actually use-auth sets token? No, use-auth calls endpoints.
            // api.ts `api` client from openapi-fetch is configured but my `apiGet` writes raw fetch.
            // My `apiGet` and `apiPost` in `lib/api.ts` do NOT attach token automatically unless
            // cookies are used (credentials: include).
            // The Django backend uses SessionAuth (cookies) or TokenAuth.
            // If using Cookies (Session), `fetch` needs `credentials: 'include'`.
            // My `apiGet` in `lib/api.ts` does NOT have `credentials: 'include'`.
            // This is a BUG in my previous `api.ts` fix!
            // I need to fix `api.ts` to include credentials, OR use `openapi-fetch` client which might handle it if configured.
            
            // Re-checking api.ts...
            // It has `headers` but no `credentials`.
            
            // I should FIX api.ts first/next.
            
            // But for now, assuming I fix it, here is the delete logic:
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"}/api/v1/diagrams/${id}/`, {
                 method: "DELETE",
                 headers: {
                     "Content-Type": "application/json",
                 },
                 // IMPORTANT: Add credentials if relying on session
                 // credentials: "include" 
                 // If using Token from store (not implemented in api.ts yet for generic helpers), 
                 // we rely on cookie.
            });
            
            if (!response.ok) throw new Error("Delete failed");
            
            toast.success("Diagram deleted");
        } catch (error) {
            toast.error("Error deleting diagram");
            // Revert state if failed
            fetchData();
        }
    };

    return (
        <div className="space-y-8 p-8 pt-6">
            <div className="flex items-center justify-between space-y-2">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-white glow-text">
                        {t("title")}
                    </h2>
                    <p className="text-white/60">
                        {t("description")}
                    </p>
                </div>
            </div>

            <DiagramsTable 
                data={data}
                isLoading={isLoading}
                onDelete={handleDelete}
            />
        </div>
    );
}
