"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import NotionDiagram from "@/components/tools/NotionDiagram";

import { useTranslations } from "next-intl";

export default function NotionERPage() {
  const t = useTranslations("tools.notionER");
  const [databases, setDatabases] = useState([]);
  const [selectedDb, setSelectedDb] = useState<string | null>(null);

  return (
    <div className="container mx-auto p-4 max-w-5xl">
      <header className="mb-8 border-b border-border pb-4">
        <h1 className="text-3xl font-bold tracking-tight">{t("title")}</h1>
        <p className="text-muted-foreground mt-2">
          {t("description")}
        </p>
      </header>
    
      <div className="grid gap-8">
        {!selectedDb ? (
          <div className="p-12 border border-dashed border-border rounded-lg text-center">
            <h3 className="text-lg font-medium mb-4">{t("selectDb")}</h3>
            <Button onClick={() => setSelectedDb("mock-id")}>
              {t("scanDemo")}
            </Button>
          </div>
        ) : (
          <NotionDiagram databaseId={selectedDb} />
        )}
      </div>
    </div>
  );
}
