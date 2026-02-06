"use client";

import { useEffect } from "react";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Dashboard error:", error);
  }, [error]);

  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 p-8">
      <h2 className="text-xl font-semibold">Something went wrong</h2>
      <p className="text-muted-foreground text-sm">
        {error.digest ? `Error ID: ${error.digest}` : "An unexpected error occurred in the dashboard."}
      </p>
      <button
        onClick={reset}
        className="rounded-md border border-border bg-background px-4 py-2 text-sm hover:bg-accent"
      >
        Try again
      </button>
    </div>
  );
}
