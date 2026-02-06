"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Key, Plus, Trash2 } from "lucide-react";
import { apiGet, apiPost, apiDelete } from "@/lib/api";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface ApiKey {
    id: string;
    name: string;
    prefix: string;
    created_at: string;
    service: string;
}

export default function ApiKeysPage() {
    const t = useTranslations("keys");
    const tc = useTranslations("common");
    const [keys, setKeys] = useState<ApiKey[]>([]);
    const [loading, setLoading] = useState(true);
    const [isCreateOpen, setIsCreateOpen] = useState(false);

    const [newKeyName, setNewKeyName] = useState("");
    const [newKeyValue, setNewKeyValue] = useState("");
    const [newKeyService, setNewKeyService] = useState("gemini");

    const fetchKeys = async () => {
        try {
            const data = await apiGet<ApiKey[]>("/api/v1/ai/keys/");
            setKeys(data || []);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchKeys();
    }, []);

    const handleCreate = async () => {
        try {
            await apiPost("/api/v1/ai/keys/", {
                name: newKeyName,
                key: newKeyValue,
                service: newKeyService
            });
            setIsCreateOpen(false);
            setNewKeyName("");
            setNewKeyValue("");
            fetchKeys();
        } catch (e) {
            console.error("Failed to create key", e);
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm(t("confirmDelete"))) return;
        try {
            await apiDelete(`/api/v1/ai/keys/${id}/`);
            fetchKeys();
        } catch (e) {
            console.error("Failed to delete key", e);
        }
    };

    return (
        <div className="container max-w-4xl py-10 space-y-8">
             <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-foreground">{t("title")}</h1>
                    <p className="text-text-subtle">{t("description")}</p>
                </div>
                <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
                    <DialogTrigger asChild>
                        <Button className="bg-purple-500 hover:bg-purple-600 gap-2">
                            <Plus className="w-4 h-4" /> {t("addKey")}
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="bg-surface-raised border-glass-border text-foreground">
                        <DialogHeader>
                            <DialogTitle>{t("addTitle")}</DialogTitle>
                            <DialogDescription>
                                {t("addDescription")}
                            </DialogDescription>
                        </DialogHeader>
                        <div className="grid gap-4 py-4">
                            <div className="grid gap-2">
                                <Label>{t("name")}</Label>
                                <Input
                                    placeholder={t("namePlaceholder")}
                                    value={newKeyName}
                                    onChange={(e) => setNewKeyName(e.target.value)}
                                    className="bg-glass-bg border-glass-border"
                                />
                            </div>
                            <div className="grid gap-2">
                                <Label>{t("service")}</Label>
                                <select
                                    className="flex h-10 w-full rounded-md border border-glass-border bg-glass-bg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-purple-500"
                                    value={newKeyService}
                                    onChange={(e) => setNewKeyService(e.target.value)}
                                >
                                    <option value="gemini">Google Gemini</option>
                                    <option value="openai">OpenAI (GPT-4)</option>
                                    <option value="anthropic">Anthropic (Claude)</option>
                                </select>
                            </div>
                            <div className="grid gap-2">
                                <Label>{t("apiKey")}</Label>
                                <Input
                                    type="password"
                                    placeholder={t("apiKeyPlaceholder")}
                                    value={newKeyValue}
                                    onChange={(e) => setNewKeyValue(e.target.value)}
                                    className="bg-glass-bg border-glass-border"
                                />
                            </div>
                        </div>
                        <DialogFooter>
                            <Button variant="ghost" onClick={() => setIsCreateOpen(false)}>{tc("cancel")}</Button>
                            <Button className="bg-purple-500" onClick={handleCreate}>{t("saveKey")}</Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>

            <div className="grid gap-4">
                {loading ? (
                    <div className="text-text-secondary">{t("loadingKeys")}</div>
                ) : keys.length === 0 ? (
                    <GlassCard className="text-center py-12">
                        <Key className="w-12 h-12 text-text-ghost mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-foreground">{t("noKeys")}</h3>
                        <p className="text-text-secondary max-w-sm mx-auto mt-2">
                            {t("noKeysDescription")}
                        </p>
                    </GlassCard>
                ) : (
                    keys.map((key) => (
                        <GlassCard key={key.id} className="flex items-center justify-between p-4">
                            <div className="flex items-center gap-4">
                                <div className="p-2 bg-purple-500/10 rounded-lg">
                                    <Key className="w-5 h-5 text-purple-400" />
                                </div>
                                <div>
                                    <h4 className="font-bold text-foreground">{key.name}</h4>
                                    <div className="flex items-center gap-2 text-xs text-text-secondary font-mono mt-1">
                                        <span className="uppercase bg-glass-bg-hover px-1.5 py-0.5 rounded">{key.service}</span>
                                        <span>&bull;</span>
                                        <span>{t("startsWith", { prefix: key.prefix })}</span>
                                    </div>
                                </div>
                            </div>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="text-error-text hover:text-error-text hover:bg-error-bg"
                                onClick={() => handleDelete(key.id)}
                            >
                                <Trash2 className="w-4 h-4" />
                            </Button>
                        </GlassCard>
                    ))
                )}
            </div>
        </div>
    );
}
