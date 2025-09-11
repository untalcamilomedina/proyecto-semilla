"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tenant, TenantCreate, TenantUpdate } from "@/types/api";
import { apiClient } from "@/lib/api-client";
import { useToast } from "@/components/ui/use-toast";
import { useEffect } from "react";

const formSchema = z.object({
  name: z.string().min(2, "El nombre debe tener al menos 2 caracteres."),
  domain: z.string().optional(),
});

interface TenantFormProps {
  tenant?: Tenant;
  isOpen: boolean;
  onClose: () => void;
}

export function TenantForm({ tenant, isOpen, onClose }: TenantFormProps) {
  const { toast } = useToast();
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      domain: "",
    },
  });

  useEffect(() => {
    if (tenant) {
      form.reset({
        name: tenant.name,
        domain: tenant.domain,
      });
    } else {
      form.reset({
        name: "",
        domain: "",
      });
    }
  }, [tenant, form]);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    try {
      if (tenant) {
        const updatedTenant: TenantUpdate = { ...values };
        await apiClient.updateTenant(tenant.id, updatedTenant);
        toast({
          title: "Inquilino actualizado",
          description: "El inquilino se ha actualizado correctamente.",
        });
      } else {
        const newTenant: TenantCreate = { ...values, slug: values.name.toLowerCase().replace(/\s/g, "-") };
        await apiClient.createTenant(newTenant);
        toast({
          title: "Inquilino creado",
          description: "El inquilino se ha creado correctamente.",
        });
      }
      onClose();
      // Aquí podrías agregar una función para refrescar la tabla
    } catch (error) {
      toast({
        title: "Error",
        description: "No se pudo guardar el inquilino.",
        variant: "destructive",
      });
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{tenant ? "Editar Inquilino" : "Crear Inquilino"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nombre</FormLabel>
                  <FormControl>
                    <Input placeholder="Nombre del inquilino" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="domain"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Dominio</FormLabel>
                  <FormControl>
                    <Input placeholder="dominio.com" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit">Guardar</Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}