"use client";

import { useTransition, useState } from "react";
import { useTranslations } from "next-intl";
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
    const t = useTranslations("members");
    const tc = useTranslations("common");
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
            toast.error(t("invalidEmail"));
            return;
        }

        if (emails.includes(email)) {
             toast.error(t("duplicateEmail"));
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
            toast.error(t("minOneEmail"));
            return;
        }

        startTransition(async () => {
            try {
                await memberService.invite({
                    emails,
                    role_slug: role,
                });
                toast.success(t("inviteSuccess", { count: emails.length }));
                onOpenChange(false);
                setEmails([]);
            } catch (error) {
                console.error(error);
                toast.error(t("errorInviting"));
            }
        });
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>{t("inviteTitle")}</DialogTitle>
                    <DialogDescription>
                        {t("inviteDescription")}
                    </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                    <div className="space-y-2">
                        <Label>{t("emails")}</Label>
                        <div className="flex flex-wrap gap-2 p-2 border rounded-md min-h-[42px]">
                            {emails.map((email) => (
                                <div key={email} className="bg-zinc-100 dark:bg-zinc-800 flex items-center gap-1 px-2 py-1 rounded text-sm group">
                                    <span>{email}</span>
                                    <button onClick={() => removeEmail(email)} className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300">
                                        <X className="h-3 w-3" />
                                    </button>
                                </div>
                            ))}
                            <input
                                className="flex-1 outline-none text-sm min-w-[120px] bg-transparent"
                                placeholder={emails.length === 0 ? t("emailsPlaceholder") : ""}
                                value={currentEmail}
                                onChange={(e) => setCurrentEmail(e.target.value)}
                                onKeyDown={handleAddEmail}
                                onBlur={(e) => {
                                    if(currentEmail) handleAddEmail(e as any)
                                }}
                            />
                        </div>
                        <p className="text-xs text-zinc-500">{t("emailsHint")}</p>
                    </div>

                    <div className="space-y-2">
                        <Label>{t("role")}</Label>
                        <Select value={role} onValueChange={setRole}>
                            <SelectTrigger>
                                <SelectValue placeholder={t("selectRole")} />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="owner">{t("roleOwner")}</SelectItem>
                                <SelectItem value="admin">{t("roleAdmin")}</SelectItem>
                                <SelectItem value="member">{t("roleMember")}</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </div>
                <DialogFooter>
                    <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isPending}>
                        {tc("cancel")}
                    </Button>
                    <Button onClick={onSubmit} disabled={isPending || emails.length === 0}>
                        {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        {t("inviteButton")}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
