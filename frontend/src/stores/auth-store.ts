import { create } from 'zustand';
import { User, UserRegister, Tenant } from '../types/api';
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
  register: (userData: UserRegister) => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
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
    isLoading: true, // Default to true to prevent race conditions on load
    error: null,

    // Actions
    setUser: (user: User | null) => set({ user, isAuthenticated: !!user }),
    
    setToken: (token: string | null) => set({ token }),


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

    login: async (email, password) => {
      set({ isLoading: true, error: null });
      try {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        await apiClient.login(formData);
        await get().refreshUser(); // This will set isAuthenticated and user info
      } catch (error: any) {
        set({
          isLoading: false,
          isAuthenticated: false,
          user: null,
          error: error.response?.data?.detail || 'Email o contraseña incorrectos.',
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
        set({ isLoading: true }); // Only set loading if a session might exist
        try {
          await get().refreshUser();
        } catch (error) {
          // The session might have expired, the state is already cleared in refreshUser
          console.warn("Initialization failed: session might be expired.");
        } finally {
          set({ isLoading: false });
        }
      } else {
        // No cookie, so no session to verify.
        set({ isAuthenticated: false, user: null, isLoading: false });
      }
    },
  })
);