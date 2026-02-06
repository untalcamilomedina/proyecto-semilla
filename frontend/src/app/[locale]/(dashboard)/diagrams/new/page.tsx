"use client";

import { useState } from "react";
import { useRouter } from "@/lib/navigation";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { ArrowRight, Check, Loader2, Database, LayoutTemplate } from "lucide-react";
import { cn } from "@/lib/utils";

const STEPS = ["Select Source", "Configuration", "Review"];

export default function ImportWizardPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [source, setSource] = useState<"notion" | "miro" | null>(null);
  const [loading, setLoading] = useState(false);

  // Form State
  const [boardId, setBoardId] = useState("");

  const handleImport = async () => {
    setLoading(true);
    try {
        let response;
        if (source === "miro") {
            // POST /api/v1/integrations/miro/import_erd/
            response = await api.POST("/api/v1/integrations/miro/import_erd/", {
                body: {
                    board_id: boardId,
                    token: "user-token" // In real app, handle token securely
                }
            } as any);
        }
        
        if (response?.data) {
            // Redirect to the new Diagram (assuming API returns it, or we create one)
            // Ideally backend returns { id: "..." }
            // For now, redirect to dashboard
            router.push("/integrations"); 
        }
    } catch (e) {
        console.error("Import failed", e);
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="container mx-auto max-w-3xl py-12 space-y-8">
      {/* Progress */}
      <div className="flex justify-between items-center mb-12">
        {STEPS.map((step, i) => (
          <div key={i} className="flex flex-col items-center gap-2">
            <div className={cn(
              "w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2",
              i <= currentStep ? "border-primary bg-primary text-primary-foreground" : "border-muted text-muted-foreground"
            )}>
              {i < currentStep ? <Check className="w-4 h-4" /> : i + 1}
            </div>
            <span className="text-xs text-muted-foreground">{step}</span>
          </div>
        ))}
      </div>

      <GlassCard className="min-h-[400px] flex flex-col">
        {currentStep === 0 && (
          <div className="space-y-6 flex-1">
            <h2 className="text-2xl font-bold">Choose Import Source</h2>
            <div className="grid grid-cols-2 gap-4">
               <button 
                  onClick={() => setSource("notion")}
                  className={cn(
                    "p-6 rounded-xl border-2 flex flex-col items-center gap-4 transition-all",
                    source === "notion" ? "border-primary bg-primary/10" : "border-border hover:border-primary/50"
                  )}
               >
                  <Database className="w-12 h-12" />
                  <span className="font-semibold">Notion Database</span>
               </button>

               <button 
                  onClick={() => setSource("miro")}
                  className={cn(
                    "p-6 rounded-xl border-2 flex flex-col items-center gap-4 transition-all",
                    source === "miro" ? "border-[#FFD02F] bg-[#FFD02F]/10" : "border-border hover:border-[#FFD02F]/50"
                  )}
               >
                  <LayoutTemplate className="w-12 h-12" />
                  <span className="font-semibold">Miro Board</span>
               </button>
            </div>
          </div>
        )}

        {currentStep === 1 && source === "miro" && (
            <div className="space-y-6 flex-1">
                <h2 className="text-2xl font-bold">Configure Miro Import</h2>
                <div className="space-y-4">
                    <label className="block text-sm font-medium">Board ID</label>
                    <input 
                        className="w-full bg-background border rounded-md p-2" 
                        placeholder="e.g. uXjVKabc123="
                        value={boardId}
                        onChange={(e) => setBoardId(e.target.value)}
                    />
                    <p className="text-xs text-muted-foreground">Found in the URL of your Miro board.</p>
                </div>
            </div>
        )}

        {/* Footer Navigation */}
        <div className="flex justify-between mt-auto pt-8 border-t border-white/10">
            <Button 
                variant="ghost" 
                onClick={() => setCurrentStep(p => Math.max(0, p - 1))}
                disabled={currentStep === 0}
            >
                Back
            </Button>

            {currentStep < STEPS.length - 1 ? (
                <Button 
                    onClick={() => setCurrentStep(p => p + 1)} 
                    disabled={!source}
                >
                    Next Step <ArrowRight className="ml-2 w-4 h-4" />
                </Button>
            ) : (
                <Button onClick={handleImport} disabled={loading}>
                    {loading && <Loader2 className="mr-2 w-4 h-4 animate-spin" />}
                    Start Import
                </Button>
            )}
        </div>
      </GlassCard>
    </div>
  );
}
