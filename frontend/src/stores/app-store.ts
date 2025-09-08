import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppConfig {
  language: string;
  timezone: string;
  dateFormat: string;
  currency: string;
}

interface AppState {
  // Configuration
  config: AppConfig;

  // App state
  currentTenant: {
    id: string;
    name: string;
    slug: string;
  } | null;

  // Navigation
  currentPage: string;
  breadcrumbs: Array<{
    label: string;
    href?: string;
  }>;

  // Actions
  setConfig: (config: Partial<AppConfig>) => void;
  setCurrentTenant: (tenant: { id: string; name: string; slug: string } | null) => void;
  setCurrentPage: (page: string) => void;
  setBreadcrumbs: (breadcrumbs: Array<{ label: string; href?: string }>) => void;
  addBreadcrumb: (breadcrumb: { label: string; href?: string }) => void;
  clearBreadcrumbs: () => void;
}

const defaultConfig: AppConfig = {
  language: 'es',
  timezone: 'America/Bogota',
  dateFormat: 'DD/MM/YYYY',
  currency: 'COP',
};

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      config: defaultConfig,
      currentTenant: null,
      currentPage: '',
      breadcrumbs: [],

      // Actions
      setConfig: (newConfig) => {
        set((state) => ({
          config: { ...state.config, ...newConfig },
        }));
      },

      setCurrentTenant: (tenant) => {
        set({ currentTenant: tenant });
      },

      setCurrentPage: (page) => {
        set({ currentPage: page });
      },

      setBreadcrumbs: (breadcrumbs) => {
        set({ breadcrumbs });
      },

      addBreadcrumb: (breadcrumb) => {
        set((state) => ({
          breadcrumbs: [...state.breadcrumbs, breadcrumb],
        }));
      },

      clearBreadcrumbs: () => {
        set({ breadcrumbs: [] });
      },
    }),
    {
      name: 'app-storage',
      partialize: (state) => ({
        config: state.config,
        currentTenant: state.currentTenant,
      }),
    }
  )
);