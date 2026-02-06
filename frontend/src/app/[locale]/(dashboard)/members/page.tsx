"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Plus, Users } from "lucide-react";
import { MembersTable } from "@/components/members/members-table";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { InviteMemberModal } from "@/components/members/invite-member-modal";

/**
 * MembersPage
 * Elite member management interface.
 * 
 * @vibe Elite - High-density information with premium aesthetics.
 */
export default function MembersPage() {
    const t = useTranslations("members");
    const [isInviteOpen, setIsInviteOpen] = useState(false);

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-2 duration-500">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20">
                        <Users className="h-6 w-6 text-blue-400" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-text-highlight">{t("title")}</h1>
                        <p className="text-sm text-text-tertiary">
                            {t("description")}
                        </p>
                    </div>
                </div>
                
                <GlassButton 
                    onClick={() => setIsInviteOpen(true)}
                    className="h-11 px-6 shadow-neon active:shadow-none"
                >
                    <Plus className="mr-2 h-4 w-4" />
                    {t("inviteButton")}
                </GlassButton>
            </div>

            <div className="relative">
                {/* Decorative glow behind table */}
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/5 rounded-full blur-[100px] pointer-events-none" />
                
                <MembersTable />
            </div>

            <InviteMemberModal 
                open={isInviteOpen} 
                onOpenChange={setIsInviteOpen} 
            />
        </div>
    );
}
