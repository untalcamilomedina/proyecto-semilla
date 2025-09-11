"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Tenant } from "@/types/api";
import { TenantActions } from "./tenant-actions";

export const columns: ColumnDef<Tenant>[] = [
  {
    accessorKey: "id",
    header: "ID",
  },
  {
    accessorKey: "name",
    header: "Nombre",
  },
  {
    accessorKey: "domain",
    header: "Dominio",
  },
  {
    id: "actions",
    cell: ({ row }) => {
      const tenant = row.original;
      return <TenantActions tenant={tenant} />;
    },
  },
];