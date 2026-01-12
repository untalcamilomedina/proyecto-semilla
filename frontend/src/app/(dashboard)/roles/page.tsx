"use client";

// Skip static generation - requires auth
export const dynamic = "force-dynamic";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useTranslations } from "next-intl";
import { Plus, Edit2, Trash2, Loader2, Download, Shield, AlertCircle } from "lucide-react";

import { apiGet, apiPost, apiPatch, apiDelete, ApiError } from "@/lib/api";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { GlassCard } from "@/components/ui/glass/GlassCard";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from "@/components/ui/dialog";
import type { Role, Permission, PaginatedResponse } from "@/types";
import { cn } from "@/lib/utils";

const roleSchema = z.object({
    name: z.string().min(1, "El nombre es requerido"),
    description: z.string().optional(),
    permissions: z.array(z.string()).optional(),
});

type RoleForm = z.infer<typeof roleSchema>;

/**
 * RolesPage
 * Elite role management interface.
 */
export default function RolesPage() {
    const t = useTranslations("roles");
    const tc = useTranslations("common");
    const [isCreateOpen, setIsCreateOpen] = useState(false);
    const [editingRole, setEditingRole] = useState<Role | null>(null);
    const [error, setError] = useState<string | null>(null);
    const queryClient = useQueryClient();

    // Fetch roles
    const { data: roles, isLoading } = useQuery({
        queryKey: ["roles"],
        queryFn: () => apiGet<PaginatedResponse<Role>>("/api/v1/roles/"),
    });

    // Fetch permissions for form
    const { data: permissions } = useQuery({
        queryKey: ["permissions"],
        queryFn: () => apiGet<PaginatedResponse<Permission>>("/api/v1/permissions/"),
    });

    // Create mutation
    const createMutation = useMutation({
        mutationFn: (data: RoleForm) => apiPost<Role>("/api/v1/roles/", data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["roles"] });
            setIsCreateOpen(false);
            reset();
            setError(null);
        },
        onError: (err: ApiError) => {
            const body = err.body as { detail?: string };
            setError(body?.detail || t("errorCreating"));
        },
    });

    // Update mutation
    const updateMutation = useMutation({
        mutationFn: ({ id, data }: { id: number; data: RoleForm }) =>
            apiPatch<Role>(`/api/v1/roles/${id}/`, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["roles"] });
            setEditingRole(null);
            reset();
            setError(null);
        },
        onError: (err: ApiError) => {
            const body = err.body as { detail?: string };
            setError(body?.detail || t("errorUpdating"));
        },
    });

    // Delete mutation
    const deleteMutation = useMutation({
        mutationFn: (id: number) => apiDelete(`/api/v1/roles/${id}/`),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["roles"] });
        },
    });

    const {
        register,
        handleSubmit,
        reset,
        setValue,
        watch,
        formState: { errors },
    } = useForm<RoleForm>({
        resolver: zodResolver(roleSchema),
        defaultValues: { permissions: [] },
    });

    const selectedPermissions = watch("permissions") || [];

    const openCreate = () => {
        reset({ name: "", description: "", permissions: [] });
        setIsCreateOpen(true);
        setError(null);
    };

    const openEdit = (role: Role) => {
        reset({
            name: role.name,
            description: role.description,
            permissions: [], // Would need to fetch role permissions
        });
        setEditingRole(role);
        setError(null);
    };

    const onSubmit = (data: RoleForm) => {
        if (editingRole) {
            updateMutation.mutate({ id: editingRole.id, data });
        } else {
            createMutation.mutate(data);
        }
    };

    const exportRoles = () => {
        const dataStr = JSON.stringify(roles?.results || [], null, 2);
        const blob = new Blob([dataStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "roles.json";
        a.click();
        URL.revokeObjectURL(url);
    };

    const isDialogOpen = isCreateOpen || editingRole !== null;
    const isPending = createMutation.isPending || updateMutation.isPending;

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/20">
                        <Shield className="h-6 w-6 text-indigo-400" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white/90">{t("title")}</h1>
                        <p className="text-sm text-white/40">
                            {t("description")}
                        </p>
                    </div>
                </div>

                <div className="flex gap-3">
                    <GlassButton variant="secondary" onClick={exportRoles} className="h-11">
                        <Download className="mr-2 h-4 w-4" />
                        {tc("export")}
                    </GlassButton>
                    <GlassButton onClick={openCreate} className="h-11">
                        <Plus className="mr-2 h-4 w-4" />
                        {t("newRole")}
                    </GlassButton>
                </div>
            </div>

            {/* Create/Edit Dialog */}
            <Dialog
                open={isDialogOpen}
                onOpenChange={(open) => {
                    if (!open) {
                        setIsCreateOpen(false);
                        setEditingRole(null);
                    }
                }}
            >
                <DialogContent className="bg-zinc-900/90 border-white/10 backdrop-blur-xl text-white">
                    <DialogHeader>
                        <DialogTitle className="text-xl font-bold">
                            {editingRole ? t("editRole") : t("createRole")}
                        </DialogTitle>
                        <DialogDescription className="text-white/50">
                            {editingRole
                                ? t("editDescription")
                                : t("createDescription")}
                        </DialogDescription>
                    </DialogHeader>

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 pt-4">
                        {error && (
                            <div className="rounded-xl bg-red-500/10 border border-red-500/20 p-4 flex items-center gap-3 text-sm text-red-400">
                                <AlertCircle className="h-4 w-4 shrink-0" />
                                {error}
                            </div>
                        )}

                        <GlassInput
                            label={t("name")}
                            placeholder={t("namePlaceholder")}
                            error={errors.name?.message}
                            {...register("name")}
                        />

                        <div className="space-y-1.5">
                            <label className="text-xs font-medium text-white/50 ml-1">
                                {t("roleDescription")}
                            </label>
                            <textarea
                                {...register("description")}
                                rows={3}
                                className={cn(
                                    "flex w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-white placeholder:text-white/20 transition-all duration-300",
                                    "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neon focus-visible:border-neon/50 shadow-sm"
                                )}
                                placeholder={t("descriptionPlaceholder")}
                            />
                        </div>

                        {permissions && permissions.results.length > 0 && (
                            <div className="space-y-3">
                                <label className="text-xs font-medium text-white/50 ml-1">
                                    {t("permissions")} ({selectedPermissions.length} {tc("confirm")})
                                </label>
                                <div className="max-h-48 overflow-y-auto border border-white/5 bg-white/[0.02] rounded-xl p-2 space-y-1 custom-scrollbar">
                                    {permissions.results.map((perm) => (
                                        <label
                                            key={perm.id}
                                            className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-white/5 cursor-pointer transition-colors"
                                        >
                                            <input
                                                type="checkbox"
                                                value={perm.codename}
                                                checked={selectedPermissions.includes(perm.codename)}
                                                onChange={(e) => {
                                                    const current = selectedPermissions || [];
                                                    if (e.target.checked) {
                                                        setValue("permissions", [...current, perm.codename]);
                                                    } else {
                                                        setValue(
                                                            "permissions",
                                                            current.filter((c) => c !== perm.codename)
                                                        );
                                                    }
                                                }}
                                                className="rounded border-white/10 bg-white/5 text-neon focus:ring-neon accent-neon"
                                            />
                                            <span className="text-sm text-white/70">{perm.name}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        )}

                        <DialogFooter className="gap-3 sm:gap-0">
                            <GlassButton
                                type="button"
                                variant="secondary"
                                className="sm:mr-3"
                                onClick={() => {
                                    setIsCreateOpen(false);
                                    setEditingRole(null);
                                }}
                            >
                                {tc("cancel")}
                            </GlassButton>
                            <GlassButton type="submit" disabled={isPending}>
                                {isPending ? tc("loading") : (editingRole ? t("saveChanges") : tc("create"))}
                            </GlassButton>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>

            {/* Roles Grid */}
            {isLoading ? (
                <div className="flex justify-center py-20">
                    <div className="relative">
                        <div className="absolute inset-0 bg-neon/20 blur-xl rounded-full" />
                        <Loader2 className="h-10 w-10 animate-spin text-neon relative z-10" />
                    </div>
                </div>
            ) : roles?.results.length === 0 ? (
                <GlassCard className="py-20 flex flex-col items-center justify-center text-center space-y-4 border-dashed border-white/10">
                    <div className="p-6 rounded-full bg-white/5">
                        <Shield className="h-12 w-12 text-white/10" />
                    </div>
                    <div>
                        <p className="text-white/40 font-medium">
                            {t("noRoles")}
                        </p>
                    </div>
                    <GlassButton onClick={openCreate} variant="secondary">
                        {t("createRole")}
                    </GlassButton>
                </GlassCard>
            ) : (
                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {roles?.results.map((role) => (
                        <GlassCard 
                            key={role.id} 
                            className="group hover:border-indigo-500/30 transition-all duration-500 bg-white/[0.01] hover:bg-white/[0.03]"
                        >
                            <div className="p-6 space-y-4">
                                <div className="flex items-start justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="h-10 w-10 rounded-xl bg-indigo-500/10 flex items-center justify-center group-hover:scale-110 transition-transform duration-500">
                                            <Shield className="h-5 w-5 text-indigo-400" />
                                        </div>
                                        <h3 className="text-lg font-bold text-white/90 group-hover:text-white transition-colors">
                                            {role.name}
                                        </h3>
                                    </div>
                                    {!role.is_system && (
                                        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                            <button
                                                className="p-2 rounded-lg hover:bg-white/10 text-white/40 hover:text-white transition-all transform hover:scale-110"
                                                onClick={() => openEdit(role)}
                                            >
                                                <Edit2 className="h-4 w-4" />
                                            </button>
                                            <button
                                                className="p-2 rounded-lg hover:bg-red-500/10 text-white/40 hover:text-red-400 transition-all transform hover:scale-110"
                                                onClick={() => deleteMutation.mutate(role.id)}
                                                disabled={deleteMutation.isPending}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </button>
                                        </div>
                                    )}
                                </div>
                                <div className="space-y-4">
                                    <p className="text-sm text-white/40 line-clamp-2 leading-relaxed h-10">
                                        {role.description || t("noDescription")}
                                    </p>
                                    <div className="pt-4 border-t border-white/5 flex items-center justify-between">
                                        {role.is_system ? (
                                            <span className="inline-flex items-center rounded-lg bg-indigo-500/10 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-indigo-400 border border-indigo-500/20">
                                                {t("system")}
                                            </span>
                                        ) : (
                                            <span className="text-[10px] font-bold uppercase tracking-wider text-white/20">
                                                Custom Role
                                            </span>
                                        )}
                                        <button 
                                            onClick={() => openEdit(role)}
                                            className="text-xs font-semibold text-neon/50 hover:text-neon transition-colors"
                                        >
                                            View Details
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </GlassCard>
                    ))}
                    
                    {/* Empty "New Role" skeleton-style card for better UX */}
                    <button 
                        onClick={openCreate}
                        className="group relative rounded-2xl border-2 border-dashed border-white/5 hover:border-white/10 transition-all duration-500 min-h-[180px] flex items-center justify-center overflow-hidden"
                    >
                        <div className="absolute inset-0 bg-white/[0.01] group-hover:bg-white/[0.03] transition-colors" />
                        <div className="relative text-center space-y-2">
                            <Plus className="h-8 w-8 text-white/10 group-hover:text-neon/50 mx-auto transition-all transform group-hover:rotate-90 group-hover:scale-125" />
                            <p className="text-sm font-medium text-white/20 group-hover:text-white/40 transition-colors">
                                {t("newRole")}
                            </p>
                        </div>
                    </button>
                </div>
            )}
        </div>
    );
}
