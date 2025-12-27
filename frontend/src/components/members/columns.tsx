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

export const columns: ColumnDef<Member>[] = [
    {
        accessorKey: "user_email",
        header: "Usuario",
        cell: ({ row }) => {
            const email = row.original.user_email;
            // Mock name/avatar logic since backend provides minimal user data for now
            const initial = email.charAt(0).toUpperCase();

            return (
                <div className="flex items-center gap-3">
                    <Avatar className="h-9 w-9">
                        <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${email}`} />
                        <AvatarFallback>{initial}</AvatarFallback>
                    </Avatar>
                    <div className="flex flex-col">
                        <span className="text-sm font-medium text-zinc-900">{email.split("@")[0]}</span>
                        <span className="text-xs text-zinc-500">{email}</span>
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
                >
                    Rol
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            );
        },
        cell: ({ row }) => {
            const role = row.original.role_slug;
            const colors: Record<string, string> = {
                owner: "bg-purple-100 text-purple-700 hover:bg-purple-100",
                admin: "bg-blue-100 text-blue-700 hover:bg-blue-100",
                member: "bg-zinc-100 text-zinc-700 hover:bg-zinc-100",
            };
            
            return <Badge className={colors[role] || colors.member}>{role}</Badge>;
        },
    },
    {
        accessorKey: "is_active",
        header: "Estado",
        cell: ({ row }) => {
            const isActive = row.original.is_active;
            return (
                <Badge variant={isActive ? "default" : "secondary"}>
                    {isActive ? "Activo" : "Inactivo"}
                </Badge>
            );
        },
    },
    {
        accessorKey: "joined_at",
        header: "Fecha de unión",
        cell: ({ row }) => {
            const date = new Date(row.original.joined_at);
            return <span className="text-sm text-zinc-500">{date.toLocaleDateString()}</span>;
        },
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const member = row.original;

            return (
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                            <span className="sr-only">Abrir menú</span>
                            <MoreHorizontal className="h-4 w-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Acciones</DropdownMenuLabel>
                        <DropdownMenuItem onClick={() => navigator.clipboard.writeText(member.user_email)}>
                            Copiar Email
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem>Editar Rol</DropdownMenuItem>
                        <DropdownMenuItem className="text-red-600">Eliminar Miembro</DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            );
        },
    },
];
