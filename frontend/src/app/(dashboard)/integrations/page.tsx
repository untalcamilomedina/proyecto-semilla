"use client";

import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { ArrowRight, CheckCircle, Database, LayoutTemplate } from "lucide-react";
import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";

type ConnectionStatus = {
    notion: boolean;
    miro: boolean;
};

export default function IntegrationsPage() {
  const [status, setStatus] = useState<ConnectionStatus>({ notion: false, miro: false });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
        try {
            const data = await apiGet<ConnectionStatus>("/api/v1/integrations/status/");
            setStatus(data);
        } catch (error) {
            console.error("Failed to fetch integration status", error);
        } finally {
            setLoading(false);
        }
    };
    fetchStatus();
  }, []);

  const handleConnect = (provider: "notion" | "miro") => {
    // Redirect to Backend OAuth Handler
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";
    window.location.href = `${API_URL}/api/v1/integrations/${provider}/connect`;
  };

  return (
    <div className="container mx-auto max-w-5xl py-12 space-y-8">
      <div className="space-y-2">
        <h1 className="text-4xl font-bold tracking-tight text-foreground">
          Integrations Hub
        </h1>
        <p className="text-muted-foreground text-lg">
          Connect your favorite tools to import/export diagrams autonomously.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Notion Card */}
        <GlassCard className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-white/10 rounded-lg">
                <Database className="w-8 h-8 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">Notion</h3>
                <p className="text-sm text-gray-400">Scan Workspaces & Sync DBs</p>
              </div>
            </div>
            {status.notion ? (
              <span className="flex items-center gap-2 text-green-400 text-sm font-medium bg-green-400/10 px-3 py-1 rounded-full">
                <CheckCircle className="w-4 h-4" /> Connected
              </span>
            ) : (
                <span className="text-sm text-gray-500">Not Connected</span>
            )}
          </div>
          
          <div className="flex-1 text-sm text-gray-300">
            Import your Notion pages as flowcharts or export your ERD diagrams directly into Notion databases.
            Supports recursive page scanning.
          </div>

          <Button 
            className="w-full bg-white text-black hover:bg-white/90"
            onClick={() => handleConnect("notion")}
            disabled={status.notion}
          >
            {status.notion ? "Manage Connection" : "Connect Notion"} <ArrowRight className="ml-2 w-4 h-4" />
          </Button>
        </GlassCard>

        {/* Miro Card */}
        <GlassCard className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-[#FFD02F]/20 rounded-lg">
                <LayoutTemplate className="w-8 h-8 text-[#FFD02F]" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">Miro</h3>
                <p className="text-sm text-gray-400">Visual Collaboration</p>
              </div>
            </div>
            {status.miro ? (
              <span className="flex items-center gap-2 text-green-400 text-sm font-medium bg-green-400/10 px-3 py-1 rounded-full">
                <CheckCircle className="w-4 h-4" /> Connected
              </span>
            ) : (
                <span className="text-sm text-gray-500">Not Connected</span>
            )}
          </div>
          
          <div className="flex-1 text-sm text-gray-300">
            Two-way sync with Miro boards. Convert sticky notes to Database schemas and visualize your architecture.
          </div>

          <Button 
            className="w-full bg-[#FFD02F] text-black hover:bg-[#FFD02F]/90"
             onClick={() => handleConnect("miro")}
             disabled={status.miro}
          >
             {status.miro ? "Manage Connection" : "Connect Miro"} <ArrowRight className="ml-2 w-4 h-4" />
          </Button>
        </GlassCard>
      </div>
    </div>
  );
}
