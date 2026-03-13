/**
 * API client with JWT authentication and auto-refresh.
 *
 * Supports dual auth:
 * - Primary: JWT Bearer token (stateless, for authenticated users)
 * - Fallback: Session + CSRF (for server-rendered pages / admin)
 *
 * Tokens are stored in memory (not localStorage) for security.
 * Refresh token is sent as httpOnly cookie or stored securely.
 */

// ── Error Class ─────────────────────────────────────────────

export class ApiError extends Error {
  constructor(
    public status: number,
    public body: unknown,
    message?: string,
  ) {
    super(message || `API Error: ${status}`);
    this.name = 'ApiError';
  }
}

// ── Token Storage (in-memory for security) ──────────────────

interface TokenPair {
  access: string;
  refresh: string;
}

let tokens: TokenPair | null = null;
let refreshPromise: Promise<TokenPair | null> | null = null;

export function getTokens(): TokenPair | null {
  return tokens;
}

export function setTokens(pair: TokenPair): void {
  tokens = pair;
}

export function clearTokens(): void {
  tokens = null;
  refreshPromise = null;
}

// ── JWT Payload Decoder ─────────────────────────────────────

export interface JwtPayload {
  user_id: number;
  email: string;
  first_name: string;
  last_name: string;
  tenant_id?: number;
  tenant_slug?: string;
  role?: string;
  exp: number;
  iat: number;
}

export function decodeToken(token: string): JwtPayload | null {
  try {
    const [, payload] = token.split('.');
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(decoded);
  } catch {
    return null;
  }
}

export function isTokenExpired(token: string, bufferSeconds = 30): boolean {
  const payload = decodeToken(token);
  if (!payload) return true;
  return Date.now() / 1000 > payload.exp - bufferSeconds;
}

// ── Token Operations ────────────────────────────────────────

export async function login(email: string, password: string): Promise<JwtPayload> {
  const res = await fetch('/api/v1/auth/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(res.status, body, 'Login failed');
  }

  const data: TokenPair = await res.json();
  setTokens(data);
  return decodeToken(data.access)!;
}

export async function refreshAccessToken(): Promise<TokenPair | null> {
  // Prevent concurrent refresh requests
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    if (!tokens?.refresh) {
      clearTokens();
      return null;
    }

    try {
      const res = await fetch('/api/v1/auth/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: tokens.refresh }),
      });

      if (!res.ok) {
        clearTokens();
        return null;
      }

      const data = await res.json();
      const newTokens: TokenPair = {
        access: data.access,
        refresh: data.refresh || tokens.refresh,
      };
      setTokens(newTokens);
      return newTokens;
    } catch {
      clearTokens();
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

export async function logout(): Promise<void> {
  clearTokens();
}

// ── CSRF (fallback for session auth) ────────────────────────

let csrfToken: string | null = null;

async function getCsrfToken(): Promise<string> {
  if (csrfToken) return csrfToken;
  const res = await fetch('/api/v1/csrf/', { credentials: 'include' });
  if (!res.ok) throw new ApiError(res.status, null, 'Failed to get CSRF token');
  const data = await res.json();
  csrfToken = data.csrfToken;
  return data.csrfToken as string;
}

export function clearCsrfToken(): void {
  csrfToken = null;
}

// ── API Request ─────────────────────────────────────────────

export interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown;
  skipAuth?: boolean;
}

export async function api<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { body, headers: customHeaders, method = 'GET', skipAuth = false, ...rest } = options;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    ...(customHeaders as Record<string, string>),
  };

  // Add JWT Bearer token if available
  if (!skipAuth && tokens?.access) {
    // Auto-refresh if expired
    if (isTokenExpired(tokens.access)) {
      const refreshed = await refreshAccessToken();
      if (!refreshed) {
        // Token expired and refresh failed — redirect to login
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        throw new ApiError(401, null, 'Session expired');
      }
    }
    headers['Authorization'] = `Bearer ${tokens.access}`;
  }

  // Add CSRF for session-based mutating requests (fallback)
  if (!tokens?.access && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method.toUpperCase())) {
    try {
      const csrf = await getCsrfToken();
      headers['X-CSRFToken'] = csrf;
    } catch {
      // Continue without CSRF
    }
  }

  const res = await fetch(path, {
    ...rest,
    method,
    headers,
    credentials: tokens?.access ? 'omit' : 'include',
    body: body ? JSON.stringify(body) : undefined,
  });

  // Handle 401 — try refresh once
  if (res.status === 401 && tokens?.access && !skipAuth) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      headers['Authorization'] = `Bearer ${refreshed.access}`;
      const retryRes = await fetch(path, {
        ...rest,
        method,
        headers,
        credentials: 'omit',
        body: body ? JSON.stringify(body) : undefined,
      });
      const retryBody = await parseResponse(retryRes);
      if (!retryRes.ok) throw new ApiError(retryRes.status, retryBody);
      return retryBody as T;
    }
  }

  const responseBody = await parseResponse(res);
  if (!res.ok) throw new ApiError(res.status, responseBody);
  return responseBody as T;
}

async function parseResponse(res: Response): Promise<unknown> {
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) return res.json();
  return res.text();
}

// ── Convenience Methods ─────────────────────────────────────

export const apiGet = <T>(path: string) => api<T>(path, { method: 'GET' });

export const apiPost = <T>(path: string, body?: unknown) =>
  api<T>(path, { method: 'POST', body });

export const apiPut = <T>(path: string, body?: unknown) =>
  api<T>(path, { method: 'PUT', body });

export const apiPatch = <T>(path: string, body?: unknown) =>
  api<T>(path, { method: 'PATCH', body });

export const apiDelete = <T>(path: string) =>
  api<T>(path, { method: 'DELETE' });
