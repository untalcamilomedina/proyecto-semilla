"use client";

import { useState } from "react";
import { MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tenant } from "@/types/api";
import { TenantForm } from "./tenant-form";
import { apiClient } from "@/lib/api-client";
import { useToast } from "@/components/ui/use-toast";

interface TenantActionsProps {
  tenant: Tenant;
}

export function TenantActions({ tenant }: TenantActionsProps) {
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const { toast } = useToast();

  const handleDelete = async () => {
    try {
      await apiClient.deleteTenant(tenant.id);
      toast({
        title: "Inquilino eliminado",
        description: `El inquilino ${tenant.name} ha sido eliminado.`,
      });
      // Aquí podrías agregar una función para refrescar la tabla
    } catch (error) {
      toast({
        title: "Error",
        description: "No se pudo eliminar el inquilino.",
        variant: "destructive",
      });
    }
  };

  return (
    <>
      <TenantForm
        tenant={tenant}
        isOpen={isEditDialogOpen}
        onClose={() => setIsEditDialogOpen(false)}
      />
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="h-8 w-8 p-0">
            <span className="sr-only">Abrir menú</span>
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuLabel>Acciones</DropdownMenuLabel>
          <DropdownMenuItem onClick={() => setIsEditDialogOpen(true)}>
            Editar
          </DropdownMenuItem>
          <DropdownMenuItem onClick={handleDelete}>Eliminar</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </>
  );
}