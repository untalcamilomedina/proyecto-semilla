"use client";

import { useTranslations } from "next-intl";
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
  const t = useTranslations("integrations");
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
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";
    window.location.href = `${API_URL}/api/v1/integrations/${provider}/connect`;
  };

  return (
    <div className="container mx-auto max-w-5xl py-12 space-y-8">
      <div className="space-y-2">
        <h1 className="text-4xl font-bold tracking-tight text-foreground">
          {t("title")}
        </h1>
        <p className="text-muted-foreground text-lg">
          {t("description")}
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <GlassCard className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-glass-bg-hover rounded-lg">
                <Database className="w-8 h-8 text-foreground" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">{t("notion.title")}</h3>
                <p className="text-sm text-text-secondary">{t("notion.subtitle")}</p>
              </div>
            </div>
            {status.notion ? (
              <span className="flex items-center gap-2 text-success-text text-sm font-medium bg-success-text/10 px-3 py-1 rounded-full">
                <CheckCircle className="w-4 h-4" /> {t("connected")}
              </span>
            ) : (
                <span className="text-sm text-text-secondary">{t("notConnected")}</span>
            )}
          </div>

          <div className="flex-1 text-sm text-text-subtle">
            {t("notion.description")}
          </div>

          <Button
            className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
            onClick={() => handleConnect("notion")}
            disabled={status.notion}
          >
            {status.notion ? t("manageConnection") : t("notion.connect")} <ArrowRight className="ml-2 w-4 h-4" />
          </Button>
        </GlassCard>

        <GlassCard className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-[#FFD02F]/20 rounded-lg">
                <LayoutTemplate className="w-8 h-8 text-[#FFD02F]" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">{t("miro.title")}</h3>
                <p className="text-sm text-text-secondary">{t("miro.subtitle")}</p>
              </div>
            </div>
            {status.miro ? (
              <span className="flex items-center gap-2 text-success-text text-sm font-medium bg-success-text/10 px-3 py-1 rounded-full">
                <CheckCircle className="w-4 h-4" /> {t("connected")}
              </span>
            ) : (
                <span className="text-sm text-text-secondary">{t("notConnected")}</span>
            )}
          </div>

          <div className="flex-1 text-sm text-text-subtle">
            {t("miro.description")}
          </div>

          <Button
            className="w-full bg-[#FFD02F] text-black hover:bg-[#FFD02F]/90"
             onClick={() => handleConnect("miro")}
             disabled={status.miro}
          >
             {status.miro ? t("manageConnection") : t("miro.connect")} <ArrowRight className="ml-2 w-4 h-4" />
          </Button>
        </GlassCard>
      </div>
    </div>
  );
}
