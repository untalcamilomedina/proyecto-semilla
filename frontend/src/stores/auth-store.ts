import { create } from 'zustand';
import { User, LoginRequest, UserRegister, Tenant } from '../types/api';
import { apiClient } from '../lib/api-client';

interface AuthState {
  // State
  user: User | null;
  token: string | null;
  activeTenant: Tenant | null;
  tenants: Tenant[];
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: UserRegister) => Promise<void>;
  logout: () => Promise<void>;
  logoutAll: () => Promise<void>;
  refreshUser: () => Promise<void>;
  switchTenant: (tenantId: string) => Promise<void>;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  initialize: () => Promise<void>;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
}

export const useAuthStore = create<AuthState>()(
  (set, get) => ({
      // Initial state
      user: null,
      token: null,
      activeTenant: null,
      tenants: [],
      isAuthenticated: false,
      isLoading: true,
      error: null,

      // Actions
      setUser: (user: User | null) => set({ user, isAuthenticated: !!user }),
      
      setToken: (token: string | null) => set({ token }),

      login: async (credentials: LoginRequest) => {
        set({ isLoading: true, error: null });
        try {
          const loginResponse = await apiClient.login(credentials);
          console.log('Login response:', loginResponse);
          // After successful login, fetch user info using cookies
          await get().refreshUser();
        } catch (error: any) {
          console.error('Login error:', error);
          set({
            isLoading: false,
            error: error.response?.data?.detail || error.detail || error.message || 'Error al iniciar sesión'
          });
          throw error;
        }
      },

      register: async (userData: UserRegister) => {
        set({ isLoading: true, error: null });
        try {
          const user = await apiClient.register(userData);
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.detail || 'Error al registrarse'
          });
          throw error;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        try {
          await apiClient.logout();
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          // Even if logout fails, clear local state
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null
          });
        }
      },

      logoutAll: async () => {
        set({ isLoading: true });
        try {
          await apiClient.logoutAll();
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: error.detail || 'Error al cerrar todas las sesiones'
          });
          throw error;
        }
      },

      refreshUser: async () => {
        set({ isLoading: true, error: null });
        try {
          const user = await apiClient.getCurrentUser();
          const tenants = await apiClient.getTenants();
          const activeTenant = user.tenant_id
            ? tenants.find((t: Tenant) => t.id === user.tenant_id) || null
            : tenants.length > 0 ? tenants[0] : null;
          
          set({
            user,
            tenants,
            activeTenant,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          set({
            user: null,
            tenants: [],
            activeTenant: null,
            isAuthenticated: false,
            isLoading: false,
            error: error.detail || 'Error al obtener información del usuario'
          });
          throw error;
        }
      },

      switchTenant: async (tenantId: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await apiClient.switchTenant(tenantId);
          // The response should contain the new token
          // but we rely on cookies, so we just need to refresh the user data
          await get().refreshUser();
          window.location.reload(); // Recargar para asegurar que todo el estado se actualice
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.detail || 'Error al cambiar de inquilino'
          });
          throw error;
        }
      },

      clearError: () => set({ error: null }),

      setLoading: (loading: boolean) => set({ isLoading: loading }),

      initialize: async () => {
        set({ isLoading: true, error: null });
        try {
          const user = await apiClient.getCurrentUser();
          const tenants = await apiClient.getTenants();
          const activeTenant = user.tenant_id
            ? tenants.find((t: Tenant) => t.id === user.tenant_id) || null
            : tenants.length > 0 ? tenants[0] : null;

          set({
            user,
            tenants,
            activeTenant,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          set({
            user: null,
            tenants: [],
            activeTenant: null,
            isAuthenticated: false,
            isLoading: false,
            error: null // Don't show error on initialization
          });
        }
      },
    })
);