import { apiGet, apiPost, apiDelete } from "@/lib/api";
import { ActivityLog, ApiKey, ApiKeyCreate, PaginatedResponse } from "@/types";

/**
 * Enterprise Service
 * Advanced management: Audit Logs and API Keys.
 * 
 * @vibe Elite - Critical infrastructure orchestration.
 */
export const enterpriseService = {
    /**
     * Get activity logs for the current tenant
     */
    getAuditLogs: (params?: Record<string, string>) => {
        const query = params ? `?${new URLSearchParams(params).toString()}` : "";
        return apiGet<PaginatedResponse<ActivityLog>>(`/activity-logs/${query}`);
    },

    /**
     * API Keys Management
     */
    getApiKeys: () => apiGet<ApiKey[]>("/api-keys/"),

    createApiKey: (data: ApiKeyCreate) => apiPost<ApiKey>("/api-keys/", data),

    revokeApiKey: (id: number) => apiPost<void>(`/api-keys/${id}/revoke/`),
};

