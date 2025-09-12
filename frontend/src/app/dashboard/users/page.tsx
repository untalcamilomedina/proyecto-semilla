"use client";

import { useState, useEffect } from "react";
import { User } from "@/types/api";
import { ColumnDef } from "@tanstack/react-table";
import { UserTable } from "./user-table";
import { UserActions } from "./user-actions";
import { apiClient } from "@/lib/api-client";

export default function UsersPage() {
  const [data, setData] = useState<User[]>([]);

  const fetchData = async () => {
    try {
      const users = await apiClient.getUsers();
      setData(users);
    } catch (error) {
      console.error("Failed to fetch users", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const columns: ColumnDef<User>[] = [
    {
      accessorKey: "id",
      header: "ID",
    },
    {
      accessorKey: "full_name",
      header: "Nombre Completo",
    },
    {
      accessorKey: "email",
      header: "Email",
    },
    {
      accessorKey: "is_active",
      header: "Activo",
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const user = row.original;
        return <UserActions user={user} onSuccess={fetchData} />;
      },
    },
  ];

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-2xl font-bold mb-4">Gestión de Usuarios</h1>
      <UserTable columns={columns} data={data} refreshData={fetchData} />
    </div>
  );
}