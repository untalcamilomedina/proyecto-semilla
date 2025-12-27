"use client";

import { MembersTable } from "@/components/members/members-table";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { useState } from "react";
import { InviteMemberModal } from "@/components/members/invite-member-modal";

export default function MembersPage() {
    const [isInviteOpen, setIsInviteOpen] = useState(false);

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-zinc-900">Miembros</h1>
                    <p className="text-sm text-zinc-500">
                        Gestiona el acceso y roles de tu equipo.
                    </p>
                </div>
                <Button onClick={() => setIsInviteOpen(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    Invitar miembro
                </Button>
            </div>

            <MembersTable />

            <InviteMemberModal 
                open={isInviteOpen} 
                onOpenChange={setIsInviteOpen} 
            />
        </div>
    );
}
