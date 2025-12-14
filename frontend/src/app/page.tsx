"use client";

import { useCallback, useState } from "react";

type ApiError = {
  status: number;
  body: unknown;
};

async function apiJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, { ...init, credentials: "include" });
  const contentType = res.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await res.json() : await res.text();
  if (!res.ok) {
    throw { status: res.status, body } satisfies ApiError;
  }
  return body as T;
}

type CsrfResponse = { csrfToken: string };
type TenantResponse = {
  id: number;
  name: string;
  slug: string;
  schema_name: string;
  plan_code: string;
  enabled_modules: string[];
  branding: Record<string, unknown>;
  domain_base: string;
};

export default function Home() {
  const [csrfToken, setCsrfToken] = useState<string>("");
  const [tenant, setTenant] = useState<TenantResponse | null>(null);
  const [error, setError] = useState<string>("");

  const loadCsrf = useCallback(async () => {
    setError("");
    try {
      const data = await apiJson<CsrfResponse>("/api/v1/csrf/");
      setCsrfToken(data.csrfToken);
    } catch (err) {
      setError(JSON.stringify(err));
    }
  }, []);

  const loadTenant = useCallback(async () => {
    setError("");
    try {
      const data = await apiJson<TenantResponse>("/api/v1/tenant/");
      setTenant(data);
    } catch (err) {
      setError(JSON.stringify(err));
    }
  }, []);

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900">
      <main className="mx-auto max-w-3xl px-6 py-14">
        <h1 className="text-2xl font-semibold">Proyecto Semilla — Frontend (Next.js)</h1>
        <p className="mt-2 text-sm text-zinc-600">
          Este frontend consume la API Django vía <code className="font-mono">/api</code> (proxy por
          rewrites). Para endpoints protegidos, inicia sesión en Django primero.
        </p>

        <div className="mt-6 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={loadCsrf}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            Obtener CSRF
          </button>
          <button
            type="button"
            onClick={loadTenant}
            className="rounded-md border border-zinc-200 bg-white px-4 py-2 text-sm font-medium hover:bg-zinc-50"
          >
            Cargar tenant
          </button>
        </div>

        {csrfToken ? (
          <div className="mt-6 rounded-lg border border-zinc-200 bg-white p-4">
            <div className="text-sm font-medium">CSRF token</div>
            <div className="mt-1 break-all font-mono text-xs text-zinc-700">{csrfToken}</div>
          </div>
        ) : null}

        {tenant ? (
          <div className="mt-6 rounded-lg border border-zinc-200 bg-white p-4">
            <div className="text-sm font-medium">Tenant</div>
            <pre className="mt-2 overflow-auto rounded bg-zinc-50 p-3 text-xs">
              {JSON.stringify(tenant, null, 2)}
            </pre>
          </div>
        ) : null}

        {error ? (
          <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        ) : null}
      </main>
    </div>
  );
}
