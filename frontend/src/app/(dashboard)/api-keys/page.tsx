"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Key, Plus, Trash2, Eye, EyeOff } from "lucide-react";
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
    service: string; // 'gemini', 'openai', etc.
}

export default function ApiKeysPage() {
    const [keys, setKeys] = useState<ApiKey[]>([]);
    const [loading, setLoading] = useState(true);
    const [isCreateOpen, setIsCreateOpen] = useState(false);
    
    // Form State
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
        if (!confirm("Are you sure? This action cannot be undone.")) return;
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
                    <h1 className="text-3xl font-bold text-white glow-text">API Keys</h1>
                    <p className="text-white/60">Manage external API keys (Gemini, OpenAI) for AI features.</p>
                </div>
                <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
                    <DialogTrigger asChild>
                        <Button className="bg-purple-500 hover:bg-purple-600 gap-2">
                            <Plus className="w-4 h-4" /> Add Key
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="bg-zinc-900 border-white/10 text-white">
                        <DialogHeader>
                            <DialogTitle>Add New API Key</DialogTitle>
                            <DialogDescription>
                                Your key will be encrypted at rest. We never display the full key again.
                            </DialogDescription>
                        </DialogHeader>
                        <div className="grid gap-4 py-4">
                            <div className="grid gap-2">
                                <Label>Name</Label>
                                <Input 
                                    placeholder="My Gemini Key" 
                                    value={newKeyName}
                                    onChange={(e) => setNewKeyName(e.target.value)}
                                    className="bg-white/5 border-white/10"
                                />
                            </div>
                            <div className="grid gap-2">
                                <Label>Service</Label>
                                <select 
                                    className="flex h-10 w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                                    value={newKeyService}
                                    onChange={(e) => setNewKeyService(e.target.value)}
                                >
                                    <option value="gemini">Google Gemini</option>
                                    <option value="openai">OpenAI (GPT-4)</option>
                                    <option value="anthropic">Anthropic (Claude)</option>
                                </select>
                            </div>
                            <div className="grid gap-2">
                                <Label>API Key</Label>
                                <Input 
                                    type="password" 
                                    placeholder="sk-..." 
                                    value={newKeyValue}
                                    onChange={(e) => setNewKeyValue(e.target.value)}
                                    className="bg-white/5 border-white/10"
                                />
                            </div>
                        </div>
                        <DialogFooter>
                            <Button variant="ghost" onClick={() => setIsCreateOpen(false)}>Cancel</Button>
                            <Button className="bg-purple-500" onClick={handleCreate}>Save Key</Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>

            <div className="grid gap-4">
                {loading ? (
                    <div className="text-white/50">Loading keys...</div>
                ) : keys.length === 0 ? (
                    <GlassCard className="text-center py-12">
                        <Key className="w-12 h-12 text-white/20 mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-white">No API Keys Found</h3>
                        <p className="text-white/50 max-w-sm mx-auto mt-2">
                            Add an API key to enable AI generation features. 
                            We support Gemini, OpenAI, and Claude.
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
                                    <h4 className="font-bold text-white">{key.name}</h4>
                                    <div className="flex items-center gap-2 text-xs text-white/50 font-mono mt-1">
                                        <span className="uppercase bg-white/10 px-1.5 py-0.5 rounded">{key.service}</span>
                                        <span>•</span>
                                        <span>Starts with {key.prefix}...</span>
                                    </div>
                                </div>
                            </div>
                            <Button 
                                variant="ghost" 
                                size="icon"
                                className="text-red-400 hover:text-red-300 hover:bg-red-400/10"
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
