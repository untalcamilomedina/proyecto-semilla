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
    getSettings: () => apiGet<Tenant>("/tenant/"),

    /**
     * Update organization branding or settings
     */
    updateSettings: (data: Partial<Tenant>) => apiPatch<Tenant>("/tenant/", data),
};
