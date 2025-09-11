"use client";

import { useEffect, useState } from "react";
import { RoleTable } from "./role-table";
import { getColumns } from "./columns";
import { apiClient } from "@/lib/api-client";
import { Role } from "@/types/api";
import { RoleForm } from "./role-form";

export default function RolesPage() {
  const [roles, setRoles] = useState<Role[]>([]);

  const fetchRoles = async () => {
    try {
      const data = await apiClient.getRoles();
      setRoles(data);
    } catch (error) {
      console.error("Failed to fetch roles:", error);
    }
  };

  useEffect(() => {
    fetchRoles();
  }, []);

  return (
    <div className="container mx-auto py-10">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Roles</h1>
        <RoleForm onSuccess={fetchRoles} />
      </div>
      <RoleTable columns={getColumns(fetchRoles)} data={roles} />
    </div>
  );
}