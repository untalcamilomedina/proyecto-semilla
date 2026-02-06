import { describe, it, expect } from "vitest";
import { apiGet, apiDelete, ApiError } from "../api";
import { server } from "@/__tests__/mocks/server";
import { http, HttpResponse } from "msw";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

describe("apiGet", () => {
    it("returns JSON data on success", async () => {
        const data = await apiGet<{ stats: { total_members: number } }>("/api/v1/dashboard/");
        expect(data.stats.total_members).toBe(5);
    });

    it("throws ApiError on failure", async () => {
        server.use(
            http.get(`${API}/api/v1/dashboard/`, () => {
                return HttpResponse.json({ detail: "Not found" }, { status: 404 });
            })
        );

        await expect(apiGet("/api/v1/dashboard/")).rejects.toThrow(ApiError);

        try {
            await apiGet("/api/v1/dashboard/");
        } catch (e) {
            expect(e).toBeInstanceOf(ApiError);
            expect((e as ApiError).status).toBe(404);
        }
    });
});

describe("apiDelete", () => {
    it("returns null on 204", async () => {
        const result = await apiDelete("/api/v1/diagrams/d1/");
        expect(result).toBeNull();
    });

    it("throws ApiError on failure", async () => {
        server.use(
            http.delete(`${API}/api/v1/diagrams/:id/`, () => {
                return HttpResponse.json({ detail: "Forbidden" }, { status: 403 });
            })
        );

        await expect(apiDelete("/api/v1/diagrams/d1/")).rejects.toThrow(ApiError);
    });
});
