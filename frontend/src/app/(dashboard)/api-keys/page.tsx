"use client";

import { useTranslations } from "next-intl";
import { enterpriseService } from "@/services/enterprise";
import { ApiKey } from "@/types";
import { useEffect, useState } from "react";
import { GlassCard } from "@/components/ui/glass/GlassCard";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { Key, Plus, Trash2, Copy, Check, ShieldAlert } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

/**
 * ApiKeysPage
 * Enterprise key management with Glassmorphism Elite.
 * 
 * @vibe Elite - Secure, developer-focused key orchestration.
 */
export default function ApiKeysPage() {
    const t = useTranslations("keys");
    const [keys, setKeys] = useState<ApiKey[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [newKeyName, setNewKeyName] = useState("");
    const [createdKey, setCreatedKey] = useState<string | null>(null);
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        fetchKeys();
    }, []);

    const fetchKeys = async () => {
        try {
            const data = await enterpriseService.getApiKeys();
            setKeys(data);
        } catch (error) {
            console.error("Failed to fetch keys:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleCreate = async () => {
        if (!newKeyName) return;
        try {
            const res = await enterpriseService.createApiKey({ name: newKeyName });
            setCreatedKey(res.key || null);
            setNewKeyName("");
            fetchKeys();
            toast.success(t("created"));
        } catch {
            toast.error("Error");
        }
    };

    const handleRevoke = async (id: number) => {
        try {
            await enterpriseService.revokeApiKey(id);
            fetchKeys();
            toast.success(t("revocationSuccess"));
        } catch {
            toast.error("Error");
        }
    };

    const copyToClipboard = () => {
        if (createdKey) {
            navigator.clipboard.writeText(createdKey);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-2xl bg-purple-500/10 border border-purple-500/20">
                        <Key className="h-6 w-6 text-purple-400" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white/90">{t("title")}</h1>
                        <p className="text-sm text-white/40">{t("description")}</p>
                    </div>
                </div>
            </div>

            <div className="grid gap-8 lg:grid-cols-3">
                {/* Create Key Card */}
                <div className="lg:col-span-1">
                    <GlassCard className="p-6 space-y-6">
                        <h2 className="text-lg font-semibold flex items-center gap-2">
                            <Plus className="h-4 w-4 text-neon" />
                            {t("createButton")}
                        </h2>
                        <div className="space-y-4">
                            <GlassInput 
                                label="Nombre de la llave"
                                placeholder={t("namePlaceholder")}
                                value={newKeyName}
                                onChange={(e) => setNewKeyName(e.target.value)}
                            />
                            <GlassButton 
                                onClick={handleCreate}
                                className="w-full"
                                disabled={!newKeyName}
                            >
                                {t("createButton")}
                            </GlassButton>
                        </div>
                    </GlassCard>
                </div>

                {/* Keys List */}
                <div className="lg:col-span-2 space-y-6">
                    {createdKey && (
                        <div className="animate-in zoom-in-95 duration-300">
                            <GlassCard className="p-6 border-neon/30 bg-neon/5 space-y-4">
                                <div className="flex items-center gap-2 text-neon text-sm font-bold">
                                    <ShieldAlert className="h-4 w-4" />
                                    {t("keyWarning")}
                                </div>
                                <div className="flex items-center gap-2">
                                    <code className="flex-1 p-3 rounded-xl bg-black/40 border border-white/10 font-mono text-neon break-all">
                                        {createdKey}
                                    </code>
                                    <GlassButton onClick={copyToClipboard} className="h-12 w-12 p-0">
                                        {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                                    </GlassButton>
                                </div>
                                <GlassButton 
                                    variant="secondary" 
                                    onClick={() => setCreatedKey(null)}
                                    className="w-full h-9 text-xs"
                                >
                                    He guardado la llave
                                </GlassButton>
                            </GlassCard>
                        </div>
                    )}

                    <div className="grid gap-4">
                        {isLoading ? (
                            <GlassCard className="flex items-center justify-center h-32 border-white/5">
                                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-neon" />
                            </GlassCard>
                        ) : keys.length === 0 ? (
                            <GlassCard className="p-12 text-center text-white/20 italic border-dashed border-white/5">
                                No hay llaves activas
                            </GlassCard>
                        ) : (
                            keys.map((key) => (
                                <GlassCard key={key.id} className="p-6 group hover:border-white/20 transition-all">
                                    <div className="flex items-center justify-between gap-4">
                                        <div className="flex items-center gap-4">
                                            <div className="p-2 rounded-lg bg-white/5">
                                                <Key className="h-4 w-4 text-white/40" />
                                            </div>
                                            <div>
                                                <h3 className="font-semibold text-white/90">{key.name}</h3>
                                                <div className="flex items-center gap-2 mt-1">
                                                    <span className="text-[10px] font-mono text-white/30 tracking-widest">{key.prefix}••••••••</span>
                                                    <Badge className={cn(
                                                        "text-[9px] px-1.5 py-0 rounded-md font-bold uppercase",
                                                        key.revoked_at ? "bg-red-500/10 text-red-500 border-red-500/20" : "bg-neon/10 text-neon border-neon/20"
                                                    )}>
                                                        {key.revoked_at ? t("revoked") : t("active")}
                                                    </Badge>
                                                </div>
                                            </div>
                                        </div>
                                        {!key.revoked_at && (
                                            <GlassButton 
                                                variant="danger" 
                                                onClick={() => handleRevoke(key.id)}
                                                className="opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8 p-0"
                                            >
                                                <Trash2 className="h-3.5 w-3.5" />
                                            </GlassButton>
                                        )}
                                    </div>
                                </GlassCard>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
