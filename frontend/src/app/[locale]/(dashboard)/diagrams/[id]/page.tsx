"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import DiagramCanvas from "@/components/diagrams/canvas";
import { GlassCard } from "@/components/ui/glass-card";
import { Loader2 } from "lucide-react";
import { components } from "@/types/api";

type Diagram = components["schemas"]["Diagram"];
// ERDSpec definition might be inside Diagram oneOf or separate component
// Assuming simplest case or using 'any' temporarily if types are strict
type ERDSpec = any; 

export default function DiagramPage() {
  const { id } = useParams() as { id: string };
  const [diagram, setDiagram] = useState<Diagram | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch Diagram logic
    // GET /api/v1/diagrams/{id}/
    const fetchDiagram = async () => {
      try {
        const { data, error } = await api.GET("/api/v1/diagrams/{id}/", {
            params: { path: { id } }
        });
        if (data) {
            setDiagram(data);
        }
      } catch (e) {
        console.error("Failed to load diagram", e);
      } finally {
        setLoading(false);
      }
    };

    if (id) fetchDiagram();
  }, [id]);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!diagram) {
    return <div>Diagram not found</div>;
  }

  // Cast Spec to ERDSpec (assuming type guard in real app)
  const spec = diagram.spec as unknown as ERDSpec;

  return (
    <div className="container mx-auto max-w-7xl py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{diagram.name}</h1>
          <p className="text-muted-foreground">{diagram.description || "No description"}</p>
        </div>
        <div className="flex gap-2">
            <span className="bg-primary/10 text-primary px-3 py-1 rounded-full text-sm font-mono">
                {diagram.type?.toUpperCase() || "DIAGRAM"}
            </span>
        </div>
      </div>

      <GlassCard className="p-0 overflow-hidden border-0">
         <DiagramCanvas spec={spec} />
      </GlassCard>
    </div>
  );
}
