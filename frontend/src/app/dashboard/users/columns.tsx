"use client";

import { ColumnDef } from "@tanstack/react-table";
import { User } from "@/types/api";
import { UserActions } from "./user-actions";

export const getColumns = (onSuccess: () => void): ColumnDef<User>[] => [
  {
    accessorKey: "id",
    header: "ID",
  },
  {
    accessorKey: "email",
    header: "Email",
  },
  {
    accessorKey: "first_name",
    header: "First Name",
  },
  {
    accessorKey: "last_name",
    header: "Last Name",
  },
  {
    accessorKey: "role_name",
    header: "Role",
  },
  {
    id: "actions",
    cell: ({ row }) => {
      const user = row.original;
      return <UserActions user={user} onSuccess={onSuccess} />;
    },
  },
];