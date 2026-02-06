"use client";

import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/use-auth";
import { usePaginatedQuery, useDeleteMutation } from "@/hooks/use-api";
import { DiagramsTable } from "@/components/diagrams/DiagramsTable";
import { Diagram } from "@/types";
import { toast } from "sonner";

export default function DiagramsPage() {
    const t = useTranslations("diagrams");
    const { user } = useAuth();

    const { data, isLoading } = usePaginatedQuery<Diagram>(
        ["diagrams"],
        "/api/v1/diagrams/",
        { enabled: !!user }
    );

    const deleteMutation = useDeleteMutation(
        (id: string) => `/api/v1/diagrams/${id}/`,
        [["diagrams"]]
    );

    const handleDelete = (id: string) => {
        if (!confirm(t("confirmDelete"))) return;
        deleteMutation.mutate(id, {
            onSuccess: () => toast.success(t("deleteSuccess")),
            onError: () => toast.error(t("deleteError")),
        });
    };

    return (
        <div className="space-y-8 p-8 pt-6">
            <div className="flex items-center justify-between space-y-2">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-foreground">
                        {t("title")}
                    </h2>
                    <p className="text-text-subtle">
                        {t("description")}
                    </p>
                </div>
            </div>

            <DiagramsTable
                data={data?.results ?? []}
                isLoading={isLoading}
                onDelete={handleDelete}
            />
        </div>
    );
}
