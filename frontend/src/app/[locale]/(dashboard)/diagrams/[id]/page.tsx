"use client";

import dynamic from "next/dynamic";
import { useParams } from "next/navigation";
import { useResourceQuery } from "@/hooks/use-api";
import { GlassCard } from "@/components/ui/glass-card";
import { Loader2 } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { components } from "@/types/api";

const DiagramCanvas = dynamic(
    () => import("@/components/diagrams/canvas"),
    {
        ssr: false,
        loading: () => <Skeleton className="h-[600px] w-full" />,
    }
);

type Diagram = components["schemas"]["Diagram"];
type ERDSpec = any;

export default function DiagramPage() {
  const { id } = useParams() as { id: string };

  const { data: diagram, isLoading } = useResourceQuery<Diagram>(
    ["diagrams", id],
    `/api/v1/diagrams/${id}/`,
    { enabled: !!id }
  );

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!diagram) {
    return <div>Diagram not found</div>;
  }

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
