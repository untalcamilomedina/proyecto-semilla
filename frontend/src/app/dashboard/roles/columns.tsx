"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Role } from "@/types/api";
import { RoleActions } from "./role-actions";

export const getColumns = (onSuccess: () => void): ColumnDef<Role>[] => [
  {
    accessorKey: "id",
    header: "ID",
  },
  {
    accessorKey: "name",
    header: "Name",
  },
  {
    accessorKey: "description",
    header: "Description",
  },
  {
    id: "actions",
    cell: ({ row }) => {
      const role = row.original;
      return <RoleActions role={role} onSuccess={onSuccess} />;
    },
  },
];