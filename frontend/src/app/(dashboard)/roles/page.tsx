"use client";

// Skip static generation - requires auth
export const dynamic = "force-dynamic";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, Edit2, Trash2, Loader2, Download, Upload, Shield } from "lucide-react";

import { apiGet, apiPost, apiPatch, apiDelete, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from "@/components/ui/dialog";
import type { Role, Permission, PaginatedResponse } from "@/types";

const roleSchema = z.object({
    name: z.string().min(1, "El nombre es requerido"),
    description: z.string().optional(),
    permissions: z.array(z.string()).optional(),
});

type RoleForm = z.infer<typeof roleSchema>;

export default function RolesPage() {
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
            setError(body?.detail || "Error al crear rol");
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
            setError(body?.detail || "Error al actualizar rol");
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
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-zinc-900">Roles</h1>
                    <p className="mt-1 text-sm text-zinc-500">
                        Gestiona los roles y permisos de tu organización
                    </p>
                </div>

                <div className="flex gap-2">
                    <Button variant="outline" onClick={exportRoles}>
                        <Download className="h-4 w-4" />
                        Exportar
                    </Button>
                    <Button onClick={openCreate}>
                        <Plus className="h-4 w-4" />
                        Nuevo Rol
                    </Button>
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
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>
                            {editingRole ? "Editar rol" : "Crear nuevo rol"}
                        </DialogTitle>
                        <DialogDescription>
                            {editingRole
                                ? "Modifica los detalles del rol"
                                : "Crea un nuevo rol para tu organización"}
                        </DialogDescription>
                    </DialogHeader>

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        {error && (
                            <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                                {error}
                            </div>
                        )}

                        <Input
                            label="Nombre"
                            placeholder="Nombre del rol"
                            error={errors.name?.message}
                            {...register("name")}
                        />

                        <div className="space-y-1.5">
                            <label className="text-sm font-medium text-zinc-700">
                                Descripción
                            </label>
                            <textarea
                                {...register("description")}
                                rows={3}
                                className="flex w-full rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                                placeholder="Descripción del rol..."
                            />
                        </div>

                        {permissions && permissions.results.length > 0 && (
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-zinc-700">
                                    Permisos ({selectedPermissions.length} seleccionados)
                                </label>
                                <div className="max-h-48 overflow-y-auto border border-zinc-200 rounded-md p-2 space-y-1">
                                    {permissions.results.map((perm) => (
                                        <label
                                            key={perm.id}
                                            className="flex items-center gap-2 p-1.5 rounded hover:bg-zinc-50 cursor-pointer"
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
                                                className="rounded border-zinc-300"
                                            />
                                            <span className="text-sm text-zinc-700">{perm.name}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        )}

                        <DialogFooter>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => {
                                    setIsCreateOpen(false);
                                    setEditingRole(null);
                                }}
                            >
                                Cancelar
                            </Button>
                            <Button type="submit" isLoading={isPending}>
                                {editingRole ? "Guardar cambios" : "Crear rol"}
                            </Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>

            {/* Roles Grid */}
            {isLoading ? (
                <div className="flex justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-zinc-400" />
                </div>
            ) : roles?.results.length === 0 ? (
                <Card>
                    <CardContent className="py-12">
                        <div className="text-center">
                            <Shield className="mx-auto h-12 w-12 text-zinc-300" />
                            <p className="mt-4 text-sm text-zinc-500">
                                No hay roles todavía. Crea el primero.
                            </p>
                        </div>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {roles?.results.map((role) => (
                        <Card key={role.id}>
                            <CardHeader className="pb-3">
                                <div className="flex items-start justify-between">
                                    <div className="flex items-center gap-2">
                                        <div className="h-8 w-8 rounded-lg bg-indigo-100 flex items-center justify-center">
                                            <Shield className="h-4 w-4 text-indigo-600" />
                                        </div>
                                        <CardTitle className="text-base">{role.name}</CardTitle>
                                    </div>
                                    {!role.is_system && (
                                        <div className="flex gap-1">
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => openEdit(role)}
                                            >
                                                <Edit2 className="h-4 w-4 text-zinc-500" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => deleteMutation.mutate(role.id)}
                                                disabled={deleteMutation.isPending}
                                            >
                                                <Trash2 className="h-4 w-4 text-red-500" />
                                            </Button>
                                        </div>
                                    )}
                                </div>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm text-zinc-500">
                                    {role.description || "Sin descripción"}
                                </p>
                                {role.is_system && (
                                    <span className="mt-2 inline-flex items-center rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-medium text-zinc-600">
                                        Sistema
                                    </span>
                                )}
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
