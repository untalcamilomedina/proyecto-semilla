"use client";

import { useCallback } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
} from 'reactflow';
import 'reactflow/dist/style.css';

const initialNodes = [
  { id: '1', position: { x: 0, y: 0 }, data: { label: 'Users DB' }, type: 'input' },
  { id: '2', position: { x: 0, y: 100 }, data: { label: 'Tasks DB' } },
];
const initialEdges = [{ id: 'e1-2', source: '1', target: '2', label: 'assigned_to' }];

export default function NotionDiagram({ databaseId }: { databaseId: string }) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback((params: any) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  return (
    <div className="h-[600px] border border-border rounded-lg bg-background">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        className="bg-gray-50 dark:bg-zinc-900"
      >
        <Controls className="!bg-background !border-border !fill-foreground" />
        <MiniMap className="!bg-background !border-border" />
        <Background gap={12} size={1} />
      </ReactFlow>
    </div>
  );
}
