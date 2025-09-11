import { create } from 'zustand';
import { User, LoginRequest, UserRegister } from '../types/api';
import { apiClient } from '../lib/api-client';

interface AuthState {
  // State
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: UserRegister) => Promise<void>;
  logout: () => Promise<void>;
  logoutAll: () => Promise<void>;
  refreshUser: () => Promise<void>;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  (set, get) => ({
      // Initial state
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
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
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: error.detail || 'Error al obtener información del usuario'
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
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null // Don't show error on initialization
          });
        }
      },
    })
);