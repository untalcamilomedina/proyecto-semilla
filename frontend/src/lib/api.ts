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

/* 
 * Middleware for Client-Side Auth (Optional usage)
 * Ideally specific hooks or contexts will call setAuthToken on login
 */
