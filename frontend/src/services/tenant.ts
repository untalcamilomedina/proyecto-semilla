import { apiGet, apiPatch } from "@/lib/api";
import { Tenant } from "@/types";

/**
 * Tenant Service
 * Handles organization settings and branding.
 */
export const tenantService = {
    /**
     * Get current organization details
     */
    getSettings: () => apiGet<Tenant>("/api/v1/tenant/"),

    /**
     * Update organization branding or settings
     */
    updateSettings: (data: Partial<Tenant>) => apiPatch<Tenant>("/api/v1/tenant/", data),
};
