"use client";

import { useEffect } from "react";

export default function AuthError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Auth error:", error);
  }, [error]);

  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4">
      <h2 className="text-xl font-semibold">Something went wrong</h2>
      <p className="text-muted-foreground text-sm">
        An error occurred during authentication.
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
