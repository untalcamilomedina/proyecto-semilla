"use client";

// Skip static generation - requires auth
export const dynamic = "force-dynamic";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, Mail, Shield, Trash2, Loader2 } from "lucide-react";

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
    DialogTrigger,
} from "@/components/ui/dialog";
import type { Membership, Role, PaginatedResponse } from "@/types";

const inviteSchema = z.object({
    emails: z.string().min(1, "Ingresa al menos un email"),
    role: z.string().min(1, "Selecciona un rol"),
});

type InviteForm = z.infer<typeof inviteSchema>;

export default function MembersPage() {
    const [isInviteOpen, setIsInviteOpen] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const queryClient = useQueryClient();

    // Fetch memberships
    const { data: memberships, isLoading } = useQuery({
        queryKey: ["memberships"],
        queryFn: () => apiGet<PaginatedResponse<Membership>>("/api/v1/memberships/"),
    });

    // Fetch roles for invite form
    const { data: roles } = useQuery({
        queryKey: ["roles"],
        queryFn: () => apiGet<PaginatedResponse<Role>>("/api/v1/roles/"),
    });

    // Invite mutation
    const inviteMutation = useMutation({
        mutationFn: (data: { emails: string[]; role: string }) =>
            apiPost("/api/v1/memberships/invite/", data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["memberships"] });
            setIsInviteOpen(false);
            setError(null);
        },
        onError: (err: ApiError) => {
            const body = err.body as { detail?: string };
            setError(body?.detail || "Error al invitar");
        },
    });

    // Delete membership mutation
    const deleteMutation = useMutation({
        mutationFn: (id: number) => apiDelete(`/api/v1/memberships/${id}/`),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["memberships"] });
        },
    });

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors },
    } = useForm<InviteForm>({
        resolver: zodResolver(inviteSchema),
        defaultValues: { role: "member" },
    });

    const onInvite = (data: InviteForm) => {
        const emails = data.emails
            .split(/[\n,]/)
            .map((e) => e.trim().toLowerCase())
            .filter((e) => e.includes("@"));
        inviteMutation.mutate({ emails, role: data.role });
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-zinc-900">Miembros</h1>
                    <p className="mt-1 text-sm text-zinc-500">
                        Gestiona los miembros de tu organización
                    </p>
                </div>

                <Dialog open={isInviteOpen} onOpenChange={setIsInviteOpen}>
                    <DialogTrigger asChild>
                        <Button>
                            <Plus className="h-4 w-4" />
                            Invitar
                        </Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Invitar miembros</DialogTitle>
                            <DialogDescription>
                                Ingresa los emails de las personas a invitar (uno por línea)
                            </DialogDescription>
                        </DialogHeader>

                        <form onSubmit={handleSubmit(onInvite)} className="space-y-4">
                            {error && (
                                <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                                    {error}
                                </div>
                            )}

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-zinc-700">
                                    Emails
                                </label>
                                <textarea
                                    {...register("emails")}
                                    rows={4}
                                    className="flex w-full rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                                    placeholder="email1@example.com&#10;email2@example.com"
                                />
                                {errors.emails && (
                                    <p className="text-sm text-red-600">{errors.emails.message}</p>
                                )}
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-zinc-700">Rol</label>
                                <select
                                    {...register("role")}
                                    className="flex h-9 w-full rounded-md border border-zinc-200 bg-white px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                                >
                                    {roles?.results.map((role) => (
                                        <option key={role.id} value={role.slug}>
                                            {role.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <DialogFooter>
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={() => {
                                        setIsInviteOpen(false);
                                        reset();
                                    }}
                                >
                                    Cancelar
                                </Button>
                                <Button type="submit" isLoading={inviteMutation.isPending}>
                                    <Mail className="h-4 w-4" />
                                    Enviar invitaciones
                                </Button>
                            </DialogFooter>
                        </form>
                    </DialogContent>
                </Dialog>
            </div>

            {/* Members Table */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg">
                        {memberships?.count || 0} miembros
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex justify-center py-8">
                            <Loader2 className="h-8 w-8 animate-spin text-zinc-400" />
                        </div>
                    ) : memberships?.results.length === 0 ? (
                        <p className="text-center text-sm text-zinc-500 py-8">
                            No hay miembros todavía
                        </p>
                    ) : (
                        <div className="divide-y divide-zinc-200">
                            {memberships?.results.map((member) => (
                                <div
                                    key={member.id}
                                    className="flex items-center justify-between py-4"
                                >
                                    <div className="flex items-center gap-3">
                                        <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                                            <span className="text-sm font-medium text-indigo-600">
                                                {member.user.email.charAt(0).toUpperCase()}
                                            </span>
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-zinc-900">
                                                {member.user.first_name || member.user.username || member.user.email}
                                            </p>
                                            <p className="text-xs text-zinc-500">{member.user.email}</p>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-3">
                                        <span className="inline-flex items-center gap-1 rounded-full bg-zinc-100 px-2.5 py-0.5 text-xs font-medium text-zinc-700">
                                            <Shield className="h-3 w-3" />
                                            {member.role_name}
                                        </span>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            onClick={() => deleteMutation.mutate(member.id)}
                                            disabled={deleteMutation.isPending}
                                        >
                                            <Trash2 className="h-4 w-4 text-red-500" />
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
