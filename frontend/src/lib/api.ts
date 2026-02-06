import createClient from "openapi-fetch";
import type { paths } from "../types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

export const api = createClient<paths>({
  baseUrl: API_URL,
});

// --- Auth token management (no middleware stacking) ---
let _authToken: string | null = null;

api.use({
  onRequest: ({ request }) => {
    if (_authToken) {
      request.headers.set("Authorization", `Bearer ${_authToken}`);
    }
    return request;
  },
});

export const setAuthToken = (token: string | null) => {
  _authToken = token;
};

// --- CSRF token management ---
let _csrfToken: string | null = null;

async function fetchCsrfToken(): Promise<string> {
  const response = await fetch(`${API_URL}/api/v1/csrf/`, {
    credentials: "include",
  });
  const data = await response.json();
  _csrfToken = data.csrfToken;
  return _csrfToken!;
}

async function getCsrfToken(): Promise<string> {
  if (!_csrfToken) {
    return fetchCsrfToken();
  }
  return _csrfToken;
}

export function resetCsrfToken() {
  _csrfToken = null;
}

// --- Custom Error Class ---
export class ApiError extends Error {
  status: number;
  body: Record<string, unknown>;

  constructor(status: number, body: Record<string, unknown>) {
    super(`API Error: ${status}`);
    this.status = status;
    this.body = body;
  }
}

// --- Helper to build headers with CSRF for mutations ---
async function mutationHeaders(): Promise<Record<string, string>> {
  const csrfToken = await getCsrfToken();
  return {
    "Content-Type": "application/json",
    Accept: "application/json",
    "X-CSRFToken": csrfToken,
  };
}

// --- Generic POST helper ---
export const apiPost = async <T = unknown>(
  endpoint: string,
  data?: unknown,
): Promise<T> => {
  const url = `${API_URL}${endpoint}`;
  const headers = await mutationHeaders();

  const response = await fetch(url, {
    method: "POST",
    headers,
    credentials: "include",
    body: data ? JSON.stringify(data) : undefined,
  });

  if (!response.ok) {
    // Reset CSRF token on 403 (might be expired)
    if (response.status === 403) {
      resetCsrfToken();
    }
    let errorBody;
    try {
      errorBody = await response.json();
    } catch {
      errorBody = { detail: response.statusText };
    }
    throw new ApiError(response.status, errorBody);
  }

  return response.json();
};

// --- Generic GET helper ---
export const apiGet = async <T>(endpoint: string): Promise<T> => {
  const url = `${API_URL}${endpoint}`;
  const headers = {
    Accept: "application/json",
  };

  const response = await fetch(url, {
    method: "GET",
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    throw new ApiError(response.status, { detail: response.statusText });
  }

  return response.json();
};

// --- Generic PATCH helper ---
export const apiPatch = async <T = unknown>(
  endpoint: string,
  data?: unknown,
): Promise<T> => {
  const url = `${API_URL}${endpoint}`;
  const headers = await mutationHeaders();

  const response = await fetch(url, {
    method: "PATCH",
    headers,
    credentials: "include",
    body: data ? JSON.stringify(data) : undefined,
  });

  if (!response.ok) {
    if (response.status === 403) {
      resetCsrfToken();
    }
    throw new ApiError(response.status, { detail: response.statusText });
  }

  return response.json();
};

// --- Generic DELETE helper ---
export const apiDelete = async (endpoint: string) => {
  const url = `${API_URL}${endpoint}`;
  const headers = await mutationHeaders();

  const response = await fetch(url, {
    method: "DELETE",
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    if (response.status === 403) {
      resetCsrfToken();
    }
    throw new ApiError(response.status, { detail: response.statusText });
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
};

export const clearCsrfToken = () => {
  resetCsrfToken();
  if (typeof document !== "undefined") {
    document.cookie = "csrftoken=; Max-Age=0; path=/";
    document.cookie = "sessionid=; Max-Age=0; path=/";
  }
};
