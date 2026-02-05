"use client";

import { useCallback, useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Edge,
  Node,
  MarkerType,
} from "reactflow";
import "reactflow/dist/style.css";
import { GlassCard } from "@/components/ui/glass-card";
import { ERDEntityNode } from "./nodes/ERDEntityNode";

// Custom node types
const nodeTypes = {
  entity: ERDEntityNode,
};

interface DiagramCanvasProps {
  spec: any; // Using any for simplicity here, but should be ERDSpec
}

export default function DiagramCanvas({ spec }: DiagramCanvasProps) {
  // 1. Transform Spec -> Nodes
  const initialNodes: Node[] = useMemo(() => {
    if (!spec || !spec.entities) return [];
    
    return spec.entities.map((entity: any, index: number) => ({
      id: entity.id, // Assuming entity.id matches relationship references
      type: "entity",
      position: { x: 250 * (index % 3), y: 150 * Math.floor(index / 3) }, // Basic grid layout
      data: { 
        label: entity.name,
        attributes: entity.attributes 
      },
    }));
  }, [spec]);

  // 2. Transform Spec -> Edges
  const initialEdges: Edge[] = useMemo(() => {
    if (!spec || !spec.relationships) return [];

    return spec.relationships.map((rel: any, index: number) => ({
      id: rel.id || `e${index}`,
      source: rel.source,
      target: rel.target,
      label: rel.cardinality || "",
      type: "smoothstep", // Orthogonal-ish
      animated: false,
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
      style: { stroke: "#fff" }, // White lines for dark mode
    }));
  }, [spec]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div className="h-[600px] w-full bg-slate-950/50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background gap={16} size={1} color="#ffffff20" />
        <Controls className="bg-white/10 border-white/10 text-white fill-white" />
        <MiniMap 
            nodeColor={() => "#ffffff40"} 
            maskColor="#00000080" 
            className="bg-black/50 border border-white/10"
        />
      </ReactFlow>
    </div>
  );
}
