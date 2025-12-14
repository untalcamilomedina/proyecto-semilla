/**
 * Typed API client for Django REST Framework backend
 * Handles CSRF, authentication, and error management
 */

export class ApiError extends Error {
    constructor(
        public status: number,
        public body: unknown,
        message?: string
    ) {
        super(message || `API Error: ${status}`);
        this.name = "ApiError";
    }
}

// Cache CSRF token
let csrfToken: string | null = null;

/**
 * Get CSRF token from Django backend
 * Caches the token for subsequent requests
 */
export async function getCsrfToken(): Promise<string> {
    if (csrfToken) return csrfToken;

    const res = await fetch("/api/v1/csrf/", { credentials: "include" });
    if (!res.ok) {
        throw new ApiError(res.status, null, "Failed to get CSRF token");
    }
    const data = await res.json();
    csrfToken = data.csrfToken;
    return data.csrfToken as string;
}

/**
 * Clear cached CSRF token (call on logout)
 */
export function clearCsrfToken(): void {
    csrfToken = null;
}

export interface RequestOptions extends Omit<RequestInit, "body"> {
    body?: unknown;
}

/**
 * Make an API request with automatic CSRF handling
 */
export async function api<T>(
    path: string,
    options: RequestOptions = {}
): Promise<T> {
    const { body, headers: customHeaders, method = "GET", ...rest } = options;

    const headers: Record<string, string> = {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(customHeaders as Record<string, string>),
    };

    // Add CSRF token for mutating requests
    if (["POST", "PUT", "PATCH", "DELETE"].includes(method.toUpperCase())) {
        try {
            const token = await getCsrfToken();
            headers["X-CSRFToken"] = token;
        } catch {
            // Continue without CSRF if we can't get it (may fail on server)
        }
    }

    const res = await fetch(path, {
        ...rest,
        method,
        headers,
        credentials: "include",
        body: body ? JSON.stringify(body) : undefined,
    });

    const contentType = res.headers.get("content-type") || "";
    const responseBody = contentType.includes("application/json")
        ? await res.json()
        : await res.text();

    if (!res.ok) {
        throw new ApiError(res.status, responseBody);
    }

    return responseBody as T;
}

// Convenience methods
export const apiGet = <T>(path: string) => api<T>(path, { method: "GET" });

export const apiPost = <T>(path: string, body?: unknown) =>
    api<T>(path, { method: "POST", body });

export const apiPut = <T>(path: string, body?: unknown) =>
    api<T>(path, { method: "PUT", body });

export const apiPatch = <T>(path: string, body?: unknown) =>
    api<T>(path, { method: "PATCH", body });

export const apiDelete = <T>(path: string) =>
    api<T>(path, { method: "DELETE" });
