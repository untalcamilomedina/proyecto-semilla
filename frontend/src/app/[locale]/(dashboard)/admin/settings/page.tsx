"use client";

import { useAuth } from "@/hooks/use-auth";
import { useTranslations } from "next-intl";
import { Shield, Key, Database, RefreshCw, CheckCircle } from "lucide-react";
import { GlassCard } from "@/components/ui/glass/GlassCard";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { redirect } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

export default function AdminSettingsPage() {
  const { user } = useAuth();
  // TODO: Move this check to middleware or server component for better security
  if (user?.email !== "untalcamilomedina@gmail.com" && !user?.is_superuser) {
    redirect("/");
  }

  const t = useTranslations("common");
  const [loading, setLoading] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500));
    toast.success("Credenciales guardadas correctamente");
    setLoading(false);
  };

  return (
    <div className="space-y-10 animate-in fade-in slide-in-from-bottom-2 duration-500">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-2xl bg-red-500/10 border border-red-500/20">
          <Shield className="h-6 w-6 text-red-500" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white/90">Superadmin Settings</h1>
          <p className="text-sm text-white/40">
            Gestión de credenciales críticas y configuración del sistema.
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* OAuth Configuration */}
        <GlassCard className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Key className="h-5 w-5 text-neon" />
              Integraciones OAuth
            </h3>
            <span className="px-2 py-1 rounded bg-neon/10 text-[10px] text-neon font-mono uppercase">
              Secure Storage
            </span>
          </div>

          <form onSubmit={handleSave} className="space-y-4">
            <div className="space-y-4 pt-2">
               <h4 className="text-sm font-medium text-white/60 uppercase tracking-wider">Notion Integration</h4>
               <GlassInput 
                  label="Client ID" 
                  type="password" 
                  placeholder="notion_client_id_..."
                  defaultValue="****"
               />
               <GlassInput 
                  label="Client Secret" 
                  type="password" 
                  placeholder="notion_client_secret_..."
                  defaultValue="****"
               />
               <GlassInput 
                  label="Redirect URI" 
                  placeholder="https://blockflow.so/api/v1/auth/notion/callback"
                  readOnly
                  className="opacity-50 cursor-not-allowed"
               />
            </div>

            <div className="space-y-4 pt-4 border-t border-white/5">
               <h4 className="text-sm font-medium text-white/60 uppercase tracking-wider">Google OAuth</h4>
               <GlassInput 
                  label="Client ID" 
                  type="password" 
                  placeholder="google_client_id_..."
                  defaultValue="****"
               />
               <GlassInput 
                  label="Client Secret" 
                  type="password" 
                  placeholder="google_client_secret_..."
                  defaultValue="****"
               />
            </div>

            <div className="pt-4 flex justify-end">
              <GlassButton type="submit" disabled={loading}>
                {loading ? (
                    <>
                        <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                        Guardando...
                    </>
                ) : (
                    <>
                        <CheckCircle className="mr-2 h-4 w-4" />
                        Guardar Credenciales
                    </>
                )}
              </GlassButton>
            </div>
          </form>
        </GlassCard>

        {/* System Status & Config */}
        <div className="space-y-6">
             <GlassCard className="p-6 space-y-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Database className="h-5 w-5 text-blue-400" />
                  DB Diagram Sync
                </h3>
                <p className="text-sm text-white/50">
                    Configuración para la sincronización automática de esquemas con DBDiagram.io.
                </p>
                <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-300 text-sm">
                    Estado: <strong>Inactivo</strong>
                </div>
                <GlassButton variant="secondary" className="w-full">
                    Configurar Token DBDiagram
                </GlassButton>
             </GlassCard>
        </div>
      </div>
    </div>
  );
}
