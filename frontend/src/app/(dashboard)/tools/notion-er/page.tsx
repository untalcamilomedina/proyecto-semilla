"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import NotionDiagram from "@/components/tools/NotionDiagram";

export default function NotionERPage() {
  const [databases, setDatabases] = useState([]);
  const [selectedDb, setSelectedDb] = useState(null);

  useEffect(() => {
    // Mock fetch for now, replace with actual API call
    // fetch("/api/v1/tools/notion/databases").then(...)
  }, []);

  return (
    <div className="container mx-auto p-4 max-w-5xl">
      <header className="mb-8 border-b border-border pb-4">
        <h1 className="text-3xl font-bold tracking-tight">Notion ER Diagram</h1>
        <p className="text-muted-foreground mt-2">
          Visualize sus bases de datos de Notion como diagramas Entidad-Relación.
        </p>
      </header>

      <div className="grid gap-8">
        {!selectedDb ? (
          <div className="p-12 border border-dashed border-border rounded-lg text-center">
            <h3 className="text-lg font-medium mb-4">Seleccione una Base de Datos</h3>
            <Button onClick={() => setSelectedDb("mock-id")}>
              Escanear Demo Database
            </Button>
          </div>
        ) : (
          <NotionDiagram databaseId={selectedDb} />
        )}
      </div>
    </div>
  );
}
