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

// Helper function to check for the session cookie
const hasSessionCookie = () => {
  if (typeof document === 'undefined') return false;
  return document.cookie.split(';').some((item) => item.trim().startsWith('access_token='));
};

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
        await apiClient.login(credentials);
        await get().refreshUser();
      } catch (error: any) {
        set({
          isLoading: false,
          error: error.response?.data?.detail || error.message || 'Error al iniciar sesión'
        });
        throw error;
      }
    },

    register: async (userData: UserRegister) => {
      set({ isLoading: true, error: null });
      try {
        const user = await apiClient.register(userData);
        set({ user, isAuthenticated: true, isLoading: false });
      } catch (error: any) {
        set({
          isLoading: false,
          error: error.response?.data?.detail || 'Error al registrarse'
        });
        throw error;
      }
    },

    logout: async () => {
      try {
        await apiClient.logout();
      } catch (error) {
        console.error("Logout API call failed, clearing state locally.", error);
      } finally {
        set({
          user: null,
          token: null,
          activeTenant: null,
          tenants: [],
          isAuthenticated: false,
          isLoading: false,
          error: null
        });
      }
    },

    logoutAll: async () => {
      try {
        await apiClient.logoutAll();
      } catch (error: any) {
        console.error("Logout All API call failed, clearing state locally.", error);
      } finally {
        set({
          user: null,
          token: null,
          activeTenant: null,
          tenants: [],
          isAuthenticated: false,
          isLoading: false,
          error: null
        });
      }
    },

    refreshUser: async () => {
      set({ isLoading: true });
      try {
        const user = await apiClient.getCurrentUser();
        const tenants = await apiClient.getUserTenants();
        const activeTenant = user.tenant_id
          ? tenants.find((t) => t.id === user.tenant_id)
          : tenants[0] || null;
        
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
          isAuthenticated: false,
          isLoading: false,
          error: 'Tu sesión ha expirado. Por favor, inicia sesión de nuevo.'
        });
        throw error;
      }
    },

    switchTenant: async (tenantId: string) => {
      set({ isLoading: true });
      try {
        await apiClient.switchTenant(tenantId);
        await get().refreshUser();
        // Opcional: forzar recarga si es necesario para limpiar estados de componentes
        // window.location.reload();
      } catch (error: any) {
        set({
          isLoading: false,
          error: error.response?.data?.detail || 'Error al cambiar de tenant'
        });
        throw error;
      }
    },

    clearError: () => set({ error: null }),

    setLoading: (loading: boolean) => set({ isLoading: loading }),

    initialize: async () => {
      if (hasSessionCookie()) {
        try {
          await get().refreshUser();
        } catch (error) {
          // La sesión podría haber expirado, el estado ya se limpia en refreshUser
          console.warn("Initialization failed: session might be expired.");
        }
      } else {
        set({ isLoading: false, isAuthenticated: false, user: null });
      }
    },
  })
);