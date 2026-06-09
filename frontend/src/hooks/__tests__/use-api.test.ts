import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";
import { describe, it, expect } from "vitest";
import { useResourceQuery, usePaginatedQuery, useDeleteMutation } from "../use-api";

function createWrapper() {
    const queryClient = new QueryClient({
        defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    });
    return function Wrapper({ children }: { children: ReactNode }) {
        return createElement(QueryClientProvider, { client: queryClient }, children);
    };
}

describe("useResourceQuery", () => {
    it("fetches and returns data", async () => {
        const { result } = renderHook(
            () => useResourceQuery<{ stats: { total_members: number } }>(
                ["dashboard"],
                "/api/v1/dashboard/"
            ),
            { wrapper: createWrapper() }
        );

        expect(result.current.isLoading).toBe(true);

        await waitFor(() => expect(result.current.isSuccess).toBe(true));

        expect(result.current.data?.stats.total_members).toBe(5);
    });

    it("respects enabled option", () => {
        const { result } = renderHook(
            () => useResourceQuery(["disabled"], "/api/v1/nothing/", { enabled: false }),
            { wrapper: createWrapper() }
        );

        expect(result.current.fetchStatus).toBe("idle");
    });
});

describe("usePaginatedQuery", () => {
    it("fetches paginated data", async () => {
        const { result } = renderHook(
            () => usePaginatedQuery<{ id: string; name: string }>(
                ["roles"],
                "/api/v1/roles/"
            ),
            { wrapper: createWrapper() }
        );

        await waitFor(() => expect(result.current.isSuccess).toBe(true));

        expect(result.current.data?.results).toHaveLength(1);
        expect(result.current.data?.results[0].name).toBe("Test Role");
    });
});

describe("useDeleteMutation", () => {
    it("accepts dynamic path function", async () => {
        const { result } = renderHook(
            () => useDeleteMutation(
                (id: string) => `/api/v1/roles/${id}/`,
                [["roles"]]
            ),
            { wrapper: createWrapper() }
        );

        result.current.mutate("r1");

        await waitFor(() => expect(result.current.isSuccess).toBe(true));
    });
});
