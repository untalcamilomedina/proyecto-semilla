"use client";

import { create } from "zustand";
import { apiGet, clearCsrfToken } from "@/lib/api";
import type { User, Tenant } from "@/types";

interface AuthState {
    user: User | null;
    tenant: Tenant | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    error: string | null;

    // Actions
    checkAuth: () => Promise<void>;
    loadTenant: () => Promise<void>;
    logout: () => Promise<void>;
    clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
    user: null,
    tenant: null,
    isLoading: true,
    isAuthenticated: false,
    error: null,

    checkAuth: async () => {
        set({ isLoading: true, error: null });
        try {
            // Use Django's built-in auth check endpoint
            const data = await apiGet<{ user: User; is_authenticated: boolean }>(
                "/api/v1/me/"
            );
            if (data.is_authenticated && data.user) {
                set({ user: data.user, isAuthenticated: true, isLoading: false });
                // Auto-load tenant after auth
                get().loadTenant();
            } else {
                set({ user: null, isAuthenticated: false, isLoading: false });
            }
        } catch {
            set({ user: null, isAuthenticated: false, isLoading: false });
        }
    },

    loadTenant: async () => {
        try {
            const tenant = await apiGet<Tenant>("/api/v1/tenant/");
            set({ tenant });
        } catch {
            set({ tenant: null });
        }
    },

    logout: async () => {
        set({ isLoading: true });
        try {
            await fetch("/api/v1/logout/", {
                method: "POST",
                credentials: "include",
            });
        } catch {
            // Ignore logout errors
        }
        clearCsrfToken();
        set({
            user: null,
            tenant: null,
            isAuthenticated: false,
            isLoading: false,
        });
    },

    clearError: () => set({ error: null }),
}));

/**
 * Hook for easy access to auth state and actions
 */
export function useAuth() {
    const {
        user,
        tenant,
        isLoading,
        isAuthenticated,
        error,
        checkAuth,
        loadTenant,
        logout,
        clearError,
    } = useAuthStore();

    return {
        user,
        tenant,
        isLoading,
        isAuthenticated,
        error,
        checkAuth,
        loadTenant,
        logout,
        clearError,
    };
}
