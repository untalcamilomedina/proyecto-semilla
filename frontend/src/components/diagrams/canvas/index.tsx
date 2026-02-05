"use client";

import { useMemo, useEffect } from "react";
import ReactFlow, { 
    Background, 
    Controls, 
    useNodesState, 
    useEdgesState,
    Node,
    Edge
} from "reactflow";
import "reactflow/dist/style.css";

import EntityNode from "@/components/diagrams/nodes/entity-node";
import type { components } from "@/types/api";

type ERDSpec = components["schemas"]["ERDSpec"];

interface DiagramCanvasProps {
    spec: ERDSpec;
}

const nodeTypes = {
    entity: EntityNode
};

export default function DiagramCanvas({ spec }: DiagramCanvasProps) {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);

    // Transform Spec -> Nodes on Mount
    useEffect(() => {
        if (!spec) return;

        // Simple Layout Calc (Grid)
        const newNodes: Node[] = spec.entities.map((ent, i) => {
            const col = i % 4;
            const row = Math.floor(i / 4);
            
            return {
                id: ent.id,
                type: 'entity',
                position: { x: col * 350, y: row * 300 },
                data: ent // Pass validated Entity Data
            };
        });

        // TODO: Transform Relationships to Edges
        // const newEdges: Edge[] = ...

        setNodes(newNodes);
    }, [spec, setNodes]);

    return (
        <div className="h-[600px] w-full rounded-lg border bg-background">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodeTypes={nodeTypes}
                fitView
            >
                <Background />
                <Controls />
            </ReactFlow>
        </div>
    );
}
