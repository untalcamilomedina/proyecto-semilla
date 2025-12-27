"use client";

import { useTransition, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { toast } from "sonner";
import { Loader2, Mail, Plus, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { memberService } from "@/services/members";

const formSchema = z.object({
    emails: z.array(z.string().email()).min(1, "Debes agregar al menos un email"),
    role: z.string().min(1, "Selecciona un rol"),
});

interface InviteMemberModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

export function InviteMemberModal({ open, onOpenChange }: InviteMemberModalProps) {
    const [isPending, startTransition] = useTransition();
    const [emails, setEmails] = useState<string[]>([]);
    const [currentEmail, setCurrentEmail] = useState("");

    const [role, setRole] = useState("member");

    const handleAddEmail = (e: React.KeyboardEvent<HTMLInputElement> | React.MouseEvent) => {
        if ('key' in e) {
            if (e.key !== "Enter" && e.key !== ",") return;
        }
        
        const email = currentEmail.trim().replace(/,$/, "");
        if (!email) return;

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            toast.error("Format de email inválido");
            return;
        }

        if (emails.includes(email)) {
             toast.error("Email ya agregado");
             return;
        }

        setEmails([...emails, email]);
        setCurrentEmail("");
    };

    const removeEmail = (emailToRemove: string) => {
        setEmails(emails.filter((e) => e !== emailToRemove));
    };

    const onSubmit = () => {
        if (emails.length === 0) {
            toast.error("Agrega al menos un email");
            return;
        }

        startTransition(async () => {
            try {
                await memberService.invite({
                    emails,
                    role_slug: role,
                });
                toast.success(`Se enviaron ${emails.length} invitaciones.`);
                onOpenChange(false);
                setEmails([]);
                // Reload logic typically handled by parent or query invalidation
                window.location.reload(); // Simple reload for now
            } catch (error) {
                console.error(error);
                toast.error("Error al enviar invitaciones.");
            }
        });
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Invitar miembros</DialogTitle>
                    <DialogDescription>
                        Envía invitaciones por correo a tus colegas para unirse a la organización.
                    </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                    <div className="space-y-2">
                        <Label>Emails</Label>
                        <div className="flex flex-wrap gap-2 p-2 border rounded-md min-h-[42px]">
                            {emails.map((email) => (
                                <div key={email} className="bg-zinc-100 flex items-center gap-1 px-2 py-1 rounded text-sm group">
                                    <span>{email}</span>
                                    <button onClick={() => removeEmail(email)} className="text-zinc-400 hover:text-zinc-600">
                                        <X className="h-3 w-3" />
                                    </button>
                                </div>
                            ))}
                            <input
                                className="flex-1 outline-none text-sm min-w-[120px] bg-transparent"
                                placeholder={emails.length === 0 ? "ejemplo@correo.com, otro@correo.com" : ""}
                                value={currentEmail}
                                onChange={(e) => setCurrentEmail(e.target.value)}
                                onKeyDown={handleAddEmail}
                                onBlur={(e) => { 
                                    if(currentEmail) handleAddEmail(e as any) 
                                }}
                            />
                        </div>
                        <p className="text-xs text-zinc-500">Presiona Enter o Coma para agregar múltiples emails.</p>
                    </div>

                    <div className="space-y-2">
                        <Label>Rol</Label>
                        <Select value={role} onValueChange={setRole}>
                            <SelectTrigger>
                                <SelectValue placeholder="Selecciona un rol" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="owner">Owner (Propietario)</SelectItem>
                                <SelectItem value="admin">Admin (Administrador)</SelectItem>
                                <SelectItem value="member">Member (Miembro)</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </div>
                <DialogFooter>
                    <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isPending}>
                        Cancelar
                    </Button>
                    <Button onClick={onSubmit} disabled={isPending || emails.length === 0}>
                        {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Invitar
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
