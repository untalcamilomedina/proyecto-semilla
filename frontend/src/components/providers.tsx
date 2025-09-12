'use client';

import { createContext, useContext, useEffect, ReactNode, useState } from 'react';
import { QueryProvider } from '../lib/query-provider';
import { useAuthStore } from '../stores/auth-store';
import { User } from '../types/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  logout: () => Promise<void>;
  logoutAll: () => Promise<void>;
  refreshUser: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

function AuthProvider({ children }: AuthProviderProps) {
  const authStore = useAuthStore();
  const [, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    // Initialize authentication state on app start
    authStore.initialize();
  }, []);

  const value = {
    user: authStore.user,
    isAuthenticated: authStore.isAuthenticated,
    isLoading: authStore.isLoading,
    logout: authStore.logout,
    logoutAll: authStore.logoutAll,
    refreshUser: authStore.refreshUser,
    clearError: authStore.clearError,
  };


  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

interface ProvidersProps {
  children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <QueryProvider>
      <AuthProvider>
        {children}
      </AuthProvider>
    </QueryProvider>
  );
}