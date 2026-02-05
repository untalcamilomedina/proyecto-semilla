"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { 
    Table, 
    TableBody, 
    TableCell, 
    TableHead, 
    TableHeader, 
    TableRow 
} from "@/components/ui/table";
import { 
    DropdownMenu, 
    DropdownMenuContent, 
    DropdownMenuItem, 
    DropdownMenuLabel, 
    DropdownMenuSeparator, 
    DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { MoreHorizontal, FileEdit, Trash, Eye, Plus } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api"; // Assuming we might add delete helper later
import { Diagram } from "@/types"; // Need to ensure Diagram type exists
import Link from "next/link";

interface DiagramsTableProps {
    data: Diagram[];
    isLoading: boolean;
    onDelete: (id: string) => void;
}

export function DiagramsTable({ data, isLoading, onDelete }: DiagramsTableProps) {
    const t = useTranslations("common");
    const tList = useTranslations("diagrams.list");
    const router = useRouter();
    const [filter, setFilter] = useState("");

    const filteredData = data.filter(item => 
        item.title.toLowerCase().includes(filter.toLowerCase())
    );

    if (isLoading) {
        return <div className="p-8 text-center text-white/50">{t("loading")}</div>;
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div className="w-72">
                    <GlassInput 
                        placeholder={t("table.searchPlaceholder")}
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                    />
                </div>
                <Link href="/diagrams/new">
                    <GlassButton>
                        <Plus className="mr-2 h-4 w-4" />
                        {t("create")}
                    </GlassButton>
                </Link>
            </div>

            <div className="rounded-md border border-white/10 bg-white/5 backdrop-blur-sm">
                <Table>
                    <TableHeader>
                        <TableRow className="border-white/10 hover:bg-white/5">
                            <TableHead className="text-white/70">{tList("name")}</TableHead>
                            <TableHead className="text-white/70">{tList("entities")}</TableHead>
                            <TableHead className="text-white/70">{tList("lastModified")}</TableHead>
                            <TableHead className="text-right text-white/70">{tList("actions")}</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {filteredData.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={4} className="h-24 text-center text-white/50">
                                    {t("table.noResults")}
                                </TableCell>
                            </TableRow>
                        ) : (
                            filteredData.map((diagram) => (
                                <TableRow key={diagram.id} className="border-white/10 hover:bg-white/5">
                                    <TableCell className="font-medium text-white">{diagram.title}</TableCell>
                                    <TableCell className="text-white/70">{diagram.entities_count || 0}</TableCell>
                                    <TableCell className="text-white/70">{new Date(diagram.updated_at).toLocaleDateString()}</TableCell>
                                    <TableCell className="text-right">
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <button className="h-8 w-8 p-0 text-white/70 hover:text-white">
                                                    <MoreHorizontal className="h-4 w-4" />
                                                </button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end" className="bg-glass-panel border-white/10 text-white backdrop-blur-xl">
                                                <DropdownMenuLabel>{t("actions")}</DropdownMenuLabel>
                                                <DropdownMenuItem 
                                                    onClick={() => router.push(`/diagrams/${diagram.id}`)}
                                                    className="cursor-pointer hover:bg-white/5"
                                                >
                                                    <Eye className="mr-2 h-4 w-4" />
                                                    View
                                                </DropdownMenuItem>
                                                <DropdownMenuItem className="cursor-pointer hover:bg-white/5">
                                                    <FileEdit className="mr-2 h-4 w-4" />
                                                    {t("edit")}
                                                </DropdownMenuItem>
                                                <DropdownMenuSeparator className="bg-white/10" />
                                                <DropdownMenuItem 
                                                    onClick={() => onDelete(diagram.id)}
                                                    className="cursor-pointer text-red-400 hover:bg-red-500/10 focus:text-red-400"
                                                >
                                                    <Trash className="mr-2 h-4 w-4" />
                                                    {t("delete")}
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
