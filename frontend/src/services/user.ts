import { apiGet, apiPatch, apiPost } from "@/lib/api";
import { User } from "@/types";

/**
 * User Service
 * Handles profile management and security.
 * 
 * @vibe Elite - Secure identity and access management.
 */
export const userService = {
    /**
     * Get current user profile
     */
    getProfile: () => apiGet<{ user: User; is_authenticated: boolean }>("/api/v1/me/"),

    /**
     * Update user profile data
     */
    updateProfile: (data: Partial<User>) => apiPatch<User>("/api/v1/me/", data),

    /**
     * Change user password
     */
    changePassword: (data: Record<string, string>) =>
        apiPost<{ detail: string }>("/api/v1/me/change_password/", data),
};
