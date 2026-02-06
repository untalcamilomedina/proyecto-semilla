"use client";

import * as React from "react";
import {
    ColumnDef,
    flexRender,
    getCoreRowModel,
    getPaginationRowModel,
    getSortedRowModel,
    getFilteredRowModel,
    SortingState,
    useReactTable,
    ColumnFiltersState,
} from "@tanstack/react-table";
import { useTranslations } from "next-intl";

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { ChevronLeft, ChevronRight, Search } from "lucide-react";

interface DataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[];
    data: TData[];
}

/**
 * DataTable Component
 * Premium table implementation with glassmorphism and i18n.
 */
export function DataTable<TData, TValue>({
    columns,
    data,
}: DataTableProps<TData, TValue>) {
    const t = useTranslations("common");
    const [sorting, setSorting] = React.useState<SortingState>([]);
    const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([]);

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        onSortingChange: setSorting,
        getSortedRowModel: getSortedRowModel(),
        onColumnFiltersChange: setColumnFilters,
        getFilteredRowModel: getFilteredRowModel(),
        state: {
            sorting,
            columnFilters,
        },
    });

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-4 py-2">
                <div className="relative w-full max-w-sm group">
                    <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-text-ghost group-focus-within:text-neon-text transition-colors" />
                    <GlassInput
                        placeholder={t("table.searchPlaceholder")}
                        value={(table.getColumn("user_email")?.getFilterValue() as string) ?? ""}
                        onChange={(event) =>
                            table.getColumn("user_email")?.setFilterValue(event.target.value)
                        }
                        className="pl-10 h-10 bg-glass-bg border-glass-border-subtle focus:border-neon-border"
                    />
                </div>
            </div>
            
            <div className="rounded-xl border border-glass-border-subtle overflow-hidden">
                <Table>
                    <TableHeader className="bg-glass-bg">
                        {table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id} className="border-glass-border-subtle hover:bg-transparent">
                                {headerGroup.headers.map((header) => {
                                    return (
                                        <TableHead key={header.id} className="text-text-tertiary font-bold text-xs uppercase tracking-wider h-12">
                                            {header.isPlaceholder
                                                ? null
                                                : flexRender(
                                                      header.column.columnDef.header,
                                                      header.getContext()
                                                  )}
                                        </TableHead>
                                    );
                                })}
                            </TableRow>
                        ))}
                    </TableHeader>
                    <TableBody>
                        {table.getRowModel().rows?.length ? (
                            table.getRowModel().rows.map((row) => (
                                <TableRow
                                    key={row.id}
                                    data-state={row.getIsSelected() && "selected"}
                                    className="border-glass-border-subtle hover:bg-glass-bg transition-colors"
                                >
                                    {row.getVisibleCells().map((cell) => (
                                        <TableCell key={cell.id} className="py-4 text-sm text-text-subtle">
                                            {flexRender(
                                                cell.column.columnDef.cell,
                                                cell.getContext()
                                            )}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell
                                    colSpan={columns.length}
                                    className="h-32 text-center text-text-quaternary font-medium"
                                >
                                    {t("table.noResults")}
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>

            <div className="flex items-center justify-between py-2">
                <p className="text-xs text-text-quaternary font-medium">
                    {t("table.paginationInfo", {
                        current: table.getState().pagination.pageIndex + 1,
                        total: table.getPageCount()
                    })}
                </p>
                <div className="flex items-center gap-2">
                    <GlassButton
                        variant="secondary"
                        className="h-9 w-9 p-0 flex items-center justify-center rounded-lg border-glass-border-subtle"
                        onClick={() => table.previousPage()}
                        disabled={!table.getCanPreviousPage()}
                    >
                        <ChevronLeft className="h-4 w-4" />
                    </GlassButton>
                    <GlassButton
                        variant="secondary"
                        className="h-9 w-9 p-0 flex items-center justify-center rounded-lg border-glass-border-subtle"
                        onClick={() => table.nextPage()}
                        disabled={!table.getCanNextPage()}
                    >
                        <ChevronRight className="h-4 w-4" />
                    </GlassButton>
                </div>
            </div>
        </div>
    );
}
