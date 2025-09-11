"use client";

import { useEffect, useState } from "react";
import { UserTable } from "./user-table";
import { getColumns } from "./columns";
import { apiClient } from "@/lib/api-client";
import { User } from "@/types/api";
import { UserForm } from "./user-form";

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);

  const fetchUsers = async () => {
    try {
      const data = await apiClient.getUsers();
      setUsers(data);
    } catch (error) {
      console.error("Failed to fetch users:", error);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <div className="container mx-auto py-10">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Users</h1>
        <UserForm onSuccess={fetchUsers} />
      </div>
      <UserTable columns={getColumns(fetchUsers)} data={users} />
    </div>
  );
}