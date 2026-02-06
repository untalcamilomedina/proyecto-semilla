"use client";

import { memo } from "react";
import { Handle, Position } from "reactflow";
import { GlassCard } from "@/components/ui/glass-card";

export const ERDEntityNode = memo(({ data }: { data: any }) => {
  return (
    <GlassCard className="min-w-[180px] p-0 overflow-hidden border border-glass-border !bg-glass-bg-strong !backdrop-blur-xl">
      {/* Header */}
      <div className="bg-glass-bg px-4 py-2 border-b border-glass-border font-bold text-foreground flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-blue-400" />
        {data.label}
      </div>
      
      {/* Attributes */}
      <div className="p-2 space-y-1">
        {data.attributes?.map((attr: any, i: number) => (
          <div key={i} className="flex justify-between text-xs px-2 py-1 hover:bg-glass-bg rounded">
            <span className="text-text-subtle font-mono">
                {attr.pk && <span className="text-yellow-400 mr-1">PK</span>}
                {attr.fk && <span className="text-blue-400 mr-1">FK</span>}
                {attr.name}
            </span>
            <span className="text-muted-foreground">{attr.type}</span>
          </div>
        ))}
      </div>

      {/* Connection Handles */}
      <Handle type="target" position={Position.Top} className="!bg-blue-500 !w-3 !h-3" />
      <Handle type="source" position={Position.Bottom} className="!bg-blue-500 !w-3 !h-3" />
    </GlassCard>
  );
});

ERDEntityNode.displayName = "ERDEntityNode";
