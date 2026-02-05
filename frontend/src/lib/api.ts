import createClient from "openapi-fetch";
import type { paths } from "../types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

export const api = createClient<paths>({
  baseUrl: API_URL,
});

// Helper to set auth token dynamically
export const setAuthToken = (token: string) => {
  api.use({
    onRequest: ({ request }) => {
        request.headers.set("Authorization", `Bearer ${token}`);
        return request;
    }
  });
};

// Custom Error Class
export class ApiError extends Error {
    status: number;
    body: any;

    constructor(status: number, body: any) {
        super(`API Error: ${status}`);
        this.status = status;
        this.body = body;
    }
}

// Generic POST helper for Auth flows (bypassing strict typing if needed)
export const apiPost = async (endpoint: string, data: any) => {
    const url = `${API_URL}${endpoint}`;
    const headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    };

    const response = await fetch(url, {
        method: "POST",
        headers,
        credentials: "include",
        body: JSON.stringify(data),
    });

    if (!response.ok) {
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

// Generic GET helper
export const apiGet = async <T>(endpoint: string): Promise<T> => {
    const url = `${API_URL}${endpoint}`;
    const headers = {
        "Accept": "application/json",
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

export const clearCsrfToken = () => {
    // Utility to clear cookies if needed, or no-op for now
    // implementation depends on auth strategy (cookies vs headers)
    if (typeof document !== "undefined") {
        document.cookie = "csrftoken=; Max-Age=0; path=/";
        document.cookie = "sessionid=; Max-Age=0; path=/";
    }
};
