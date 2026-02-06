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
    getProfile: () => apiGet<{ user: User; is_authenticated: boolean }>("/me/"),

    /**
     * Update user profile data
     */
    updateProfile: (data: Partial<User>) => apiPatch<User>("/me/", data),

    /**
     * Change user password
     */
    changePassword: (data: Record<string, string>) =>
        apiPost<{ detail: string }>("/me/change_password/", data),
};
