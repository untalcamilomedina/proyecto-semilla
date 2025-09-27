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
import { User } from "@/types/api";
import { apiClient } from "@/lib/api-client";
import { useToast } from "@/components/ui/use-toast";
import { useEffect } from "react";
import { useAuthStore } from "@/stores/auth-store";

const formSchema = z.object({
  email: z.string().email("Email inválido"),
  first_name: z.string().min(2, "El nombre es demasiado corto"),
  last_name: z.string().optional(),
  password: z.string().optional(),
});

interface UserFormProps {
  user?: User | null;
  isOpen: boolean;
  onClose: () => void;
}

export function UserForm({ user, isOpen, onClose }: UserFormProps) {
  const { toast } = useToast();
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      first_name: "",
      last_name: "",
      password: "",
    },
  });

  const { activeTenant } = useAuthStore();

  useEffect(() => {
    if (user) {
      form.reset({
        email: user.email,
        first_name: user.first_name ?? "",
        last_name: user.last_name ?? "",
        password: "",
      });
    } else {
      form.reset({
        email: "",
        first_name: "",
        last_name: "",
        password: "",
      });
    }
  }, [user, form]);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    try {
      if (user) {
        await apiClient.updateUser(user.id, {
          email: values.email,
          first_name: values.first_name,
          last_name: values.last_name,
        });
        toast({ title: "Usuario actualizado" });
      } else {
        if (!values.password || values.password.length < 6) {
          toast({
            title: "Contraseña requerida",
            description: "La contraseña debe tener al menos 6 caracteres.",
            variant: "destructive",
          });
          return;
        }

        if (!activeTenant?.id) {
          toast({
            title: "Selecciona un tenant",
            description: "Debes tener un tenant activo para crear usuarios.",
            variant: "destructive",
          });
          return;
        }

        await apiClient.createUser({
          email: values.email,
          first_name: values.first_name,
          last_name: values.last_name,
          password: values.password,
          tenant_id: activeTenant.id,
          role_ids: [],
        });
        toast({ title: "Usuario creado" });
      }
      onClose();
    } catch {
      toast({
        title: "Error",
        description: "No se pudo guardar el usuario.",
        variant: "destructive",
      });
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{user ? "Editar Usuario" : "Crear Usuario"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input placeholder="user@example.com" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="first_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nombre</FormLabel>
                  <FormControl>
                    <Input placeholder="Nombre" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="last_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Apellido</FormLabel>
                  <FormControl>
                    <Input placeholder="Apellido" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Contraseña</FormLabel>
                  <FormControl>
                    <Input type="password" placeholder={user ? "Dejar en blanco para mantener" : "******"} {...field} />
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
