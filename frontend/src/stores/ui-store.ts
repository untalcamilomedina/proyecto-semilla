import { create } from 'zustand';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface LoadingState {
  id: string;
  message?: string;
}

interface UIState {
  // Notifications
  notifications: Notification[];

  // Loading states
  loadingStates: LoadingState[];
  globalLoading: boolean;

  // UI state
  sidebarOpen: boolean;
  theme: 'light' | 'dark' | 'system';

  // Actions
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;

  setLoading: (id: string, loading: boolean, message?: string) => void;
  removeLoading: (id: string) => void;
  setGlobalLoading: (loading: boolean) => void;

  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}

export const useUIStore = create<UIState>((set, get) => ({
  // Initial state
  notifications: [],
  loadingStates: [],
  globalLoading: false,
  sidebarOpen: true,
  theme: 'system',

  // Notification actions
  addNotification: (notification) => {
    const id = Date.now().toString();
    const newNotification: Notification = {
      id,
      duration: 5000,
      ...notification,
    };

    set((state) => ({
      notifications: [...state.notifications, newNotification],
    }));

    // Auto remove after duration
    if (newNotification.duration && newNotification.duration > 0) {
      setTimeout(() => {
        get().removeNotification(id);
      }, newNotification.duration);
    }
  },

  removeNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    }));
  },

  clearNotifications: () => {
    set({ notifications: [] });
  },

  // Loading actions
  setLoading: (id, loading, message) => {
    set((state) => {
      if (loading) {
        const existingIndex = state.loadingStates.findIndex((ls) => ls.id === id);
        if (existingIndex >= 0) {
          // Update existing
          const newStates = [...state.loadingStates];
          newStates[existingIndex] = { id, message };
          return { loadingStates: newStates };
        } else {
          // Add new
          return {
            loadingStates: [...state.loadingStates, { id, message }],
          };
        }
      } else {
        // Remove
        return {
          loadingStates: state.loadingStates.filter((ls) => ls.id !== id),
        };
      }
    });
  },

  removeLoading: (id) => {
    set((state) => ({
      loadingStates: state.loadingStates.filter((ls) => ls.id !== id),
    }));
  },

  setGlobalLoading: (loading) => {
    set({ globalLoading: loading });
  },

  // UI actions
  toggleSidebar: () => {
    set((state) => ({ sidebarOpen: !state.sidebarOpen }));
  },

  setSidebarOpen: (open) => {
    set({ sidebarOpen: open });
  },

  setTheme: (theme) => {
    set({ theme });
    // Apply theme to document (only on client side)
    if (typeof window !== 'undefined') {
      const root = document.documentElement;
      if (theme === 'dark') {
        root.classList.add('dark');
      } else if (theme === 'light') {
        root.classList.remove('dark');
      } else {
        // system
        const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        if (systemTheme === 'dark') {
          root.classList.add('dark');
        } else {
          root.classList.remove('dark');
        }
      }
    }
  },
}));

// Helper hooks
export const useLoading = (id: string) => {
  const loadingStates = useUIStore((state) => state.loadingStates);
  return loadingStates.some((ls) => ls.id === id);
};

export const useLoadingMessage = (id: string) => {
  const loadingStates = useUIStore((state) => state.loadingStates);
  return loadingStates.find((ls) => ls.id === id)?.message;
};