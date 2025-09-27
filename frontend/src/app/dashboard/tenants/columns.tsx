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
    accessorKey: "description",
    header: "Descripción",
  },
  {
    id: "actions",
    cell: ({ row }) => {
      const tenant = row.original;
      return <TenantActions tenant={tenant} />;
    },
  },
];
