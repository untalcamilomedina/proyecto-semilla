"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, apiGet, apiPost, apiPatch, apiDelete, ApiError } from "@/lib/api";
import type { PaginatedResponse } from "@/types";

/**
 * Generic hook for fetching paginated data
 */
export function usePaginatedQuery<T>(
    key: string[],
    path: string,
    options?: { enabled?: boolean }
) {
    return useQuery<PaginatedResponse<T>, ApiError>({
        queryKey: key,
        queryFn: () => apiGet<PaginatedResponse<T>>(path),
        ...options,
    });
}

/**
 * Generic hook for fetching single resource
 */
export function useResourceQuery<T>(
    key: string[],
    path: string,
    options?: { enabled?: boolean }
) {
    return useQuery<T, ApiError>({
        queryKey: key,
        queryFn: () => apiGet<T>(path),
        ...options,
    });
}

/**
 * Generic hook for creating a resource
 */
export function useCreateMutation<TData, TResponse = TData>(
    path: string,
    invalidateKeys?: string[][]
) {
    const queryClient = useQueryClient();

    return useMutation<TResponse, ApiError, TData>({
        mutationFn: (data) => apiPost<TResponse>(path, data),
        onSuccess: () => {
            invalidateKeys?.forEach((key) => {
                queryClient.invalidateQueries({ queryKey: key });
            });
        },
    });
}

/**
 * Generic hook for updating a resource
 */
export function useUpdateMutation<TData, TResponse = TData>(
    path: string,
    invalidateKeys?: string[][]
) {
    const queryClient = useQueryClient();

    return useMutation<TResponse, ApiError, TData>({
        mutationFn: (data) => apiPatch<TResponse>(path, data),
        onSuccess: () => {
            invalidateKeys?.forEach((key) => {
                queryClient.invalidateQueries({ queryKey: key });
            });
        },
    });
}

/**
 * Generic hook for deleting a resource
 */
export function useDeleteMutation(path: string, invalidateKeys?: string[][]) {
    const queryClient = useQueryClient();

    return useMutation<void, ApiError, void>({
        mutationFn: () => apiDelete(path),
        onSuccess: () => {
            invalidateKeys?.forEach((key) => {
                queryClient.invalidateQueries({ queryKey: key });
            });
        },
    });
}

// Re-export for convenience
export { api, apiGet, apiPost, apiPatch, apiDelete, ApiError };
