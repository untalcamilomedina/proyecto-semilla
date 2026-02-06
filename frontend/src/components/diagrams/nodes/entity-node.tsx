import { memo } from "react";
import { Handle, Position } from "reactflow";
import { cn } from "@/lib/utils";
import { Database } from "lucide-react";

// Types derived from our SDK
// Types derived from our SDK
// import type { components } from "@/types/api";

type ERDEntity = {
    id: string | number;
    name: string;
    attributes: Array<{
        name: string;
        type: string;
        pk?: boolean;
        fk?: boolean;
    }>;
};

interface EntityNodeProps {
  data: ERDEntity;
}

const EntityNode = memo(({ data }: EntityNodeProps) => {
  return (
    <div className="min-w-[200px] overflow-hidden rounded-md border border-border bg-card shadow-sm">
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-border bg-muted/50 px-3 py-2">
        <Database className="h-4 w-4 text-primary" />
        <span className="text-sm font-semibold">{data.name}</span>
      </div>

      {/* Attributes List */}
      <div className="p-2">
        <ul className="space-y-1">
          {data.attributes.map((attr, i) => (
            <li key={i} className="flex items-center justify-between text-xs">
              <span className={cn(attr.pk && "font-bold text-primary")}>
                {attr.pk && "🔑 "}
                {attr.name}
              </span>
              <span className="text-muted-foreground">{attr.type}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Connectors (Handles) */}
      <Handle type="target" position={Position.Left} className="!bg-primary" />
      <Handle type="source" position={Position.Right} className="!bg-primary" />
    </div>
  );
});

EntityNode.displayName = "EntityNode";
export default EntityNode;
