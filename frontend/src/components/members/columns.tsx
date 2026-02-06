"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Member } from "@/types/member";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoreHorizontal, ArrowUpDown } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";

export const getColumns = (t: any): ColumnDef<Member>[] => [
    {
        accessorKey: "user_email",
        header: t("name") || "Usuario",
        cell: ({ row }) => {
            const email = row.original.user_email;
            const initial = email.charAt(0).toUpperCase();

            return (
                <div className="flex items-center gap-3">
                    <Avatar className="h-10 w-10 border border-glass-border rounded-xl overflow-hidden">
                        <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${email}`} />
                        <AvatarFallback className="bg-neon-bg text-neon-text font-bold">{initial}</AvatarFallback>
                    </Avatar>
                    <div className="flex flex-col">
                        <span className="text-sm font-semibold text-text-highlight">{email.split("@")[0]}</span>
                        <span className="text-[10px] text-text-quaternary font-mono">{email}</span>
                    </div>
                </div>
            );
        },
    },
    {
        accessorKey: "role_slug",
        header: ({ column }) => {
            return (
                <Button
                    variant="ghost"
                    onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                    className="hover:bg-glass-bg hover:text-foreground"
                >
                    {t("role") || "Rol"}
                    <ArrowUpDown className="ml-2 h-3.5 w-3.5 opacity-50" />
                </Button>
            );
        },
        cell: ({ row }) => {
            const role = row.original.role_slug;
            const colors: Record<string, string> = {
                owner: "bg-purple-500/10 text-purple-400 border-purple-500/20",
                admin: "bg-blue-500/10 text-blue-400 border-blue-500/20",
                member: "bg-glass-bg text-text-subtle border-glass-border",
            };

            return (
                <Badge className={cn("rounded-lg px-2.5 py-0.5 border font-medium text-[11px]", colors[role] || colors.member)}>
                    {role}
                </Badge>
            );
        },
    },
    {
        accessorKey: "is_active",
        header: t("status") || "Estado",
        cell: ({ row }) => {
            const isActive = row.original.is_active;
            return (
                <Badge className={cn(
                    "rounded-full px-2 py-0.5 border text-[10px] font-bold uppercase tracking-wider",
                    isActive
                        ? "bg-neon-bg text-neon-text border-neon-border shadow-neon"
                        : "bg-muted text-muted-foreground border-border"
                )}>
                    {isActive ? t("active") || "Activo" : t("inactive") || "Inactivo"}
                </Badge>
            );
        },
    },
    {
        accessorKey: "joined_at",
        header: t("since") || "Desde",
        cell: ({ row }) => {
            const date = new Date(row.original.joined_at);
            return <span className="text-sm text-text-tertiary font-mono uppercase text-[11px] tracking-tight">{date.toLocaleDateString()}</span>;
        },
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const member = row.original;

            return (
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0 hover:bg-glass-bg hover:text-foreground">
                            <span className="sr-only">Menu</span>
                            <MoreHorizontal className="h-4 w-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="bg-surface-raised border-glass-border backdrop-blur-xl text-foreground">
                        <DropdownMenuLabel className="text-text-tertiary text-xs font-medium uppercase tracking-widest">{t("actions") || "Acciones"}</DropdownMenuLabel>
                        <DropdownMenuItem
                            onClick={() => navigator.clipboard.writeText(member.user_email)}
                            className="focus:bg-glass-bg focus:text-foreground cursor-pointer"
                        >
                            {t("copyEmail") || "Copiar Email"}
                        </DropdownMenuItem>
                        <DropdownMenuSeparator className="bg-glass-border-subtle" />
                        <DropdownMenuItem className="focus:bg-glass-bg focus:text-foreground cursor-pointer">{t("editRole") || "Editar Rol"}</DropdownMenuItem>
                        <DropdownMenuItem className="text-error-text focus:bg-error-bg focus:text-error-text cursor-pointer">{t("remove") || "Eliminar"}</DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            );
        },
    },
];
