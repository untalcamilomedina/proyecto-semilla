'use client';

import { useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';

export function useAuth() {
  const router = useRouter();
  const {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    refreshUser,
    initialize,
    clearError
  } = useAuthStore();

  // Inicializar el estado de autenticación al montar
  useEffect(() => {
    initialize();
  }, []);

  // Función para verificar si el usuario está autenticado
  const checkAuth = useCallback(async () => {
    try {
      if (!isAuthenticated && !isLoading) {
        await refreshUser();
      }
      return true;
    } catch (error) {
      console.error('Error checking authentication:', error);
      return false;
    }
  }, [isAuthenticated, isLoading, refreshUser]);

  // Función mejorada de logout con redirección
  const handleLogout = useCallback(async () => {
    try {
      await logout();
      router.push('/login');
    } catch (error) {
      console.error('Error during logout:', error);
      // Incluso si hay error, redirigir al login
      router.push('/login');
    }
  }, [logout, router]);

  // Función para validar el token con el backend
  const validateToken = useCallback(async (): Promise<boolean> => {
    try {
      await refreshUser();
      return true;
    } catch (error) {
      console.error('Token validation failed:', error);
      return false;
    }
  }, [refreshUser]);

  // Función para requerir autenticación (útil para componentes protegidos)
  const requireAuth = useCallback(() => {
    if (!isAuthenticated && !isLoading) {
      router.push('/login');
      return false;
    }
    return true;
  }, [isAuthenticated, isLoading, router]);

  // Función para obtener el token actual (útil para peticiones manuales)
  const getToken = useCallback((): string | null => {
    // Primero intentar obtener de las cookies (más seguro)
    if (typeof window !== 'undefined') {
      const cookies = document.cookie.split(';');
      const tokenCookie = cookies.find(cookie => cookie.trim().startsWith('access_token='));
      if (tokenCookie) {
        return tokenCookie.split('=')[1];
      }
    }
    // Fallback al token del store
    return token;
  }, [token]);

  // Función para verificar permisos específicos
  // Por ahora retorna false ya que el User no tiene permisos directamente
  // Los permisos deberían obtenerse del rol del usuario
  const hasPermission = useCallback((permission: string): boolean => {
    // TODO: Implementar cuando se agregue la funcionalidad de obtener permisos del rol
    return false;
  }, []);

  // Función para verificar roles
  const hasRole = useCallback((roleName: string): boolean => {
    if (!user || !user.role_name) return false;
    return user.role_name === roleName;
  }, [user]);

  return {
    // Estado
    user,
    isAuthenticated,
    isLoading,
    error,
    
    // Funciones principales
    login,
    logout: handleLogout,
    checkAuth,
    validateToken,
    requireAuth,
    clearError,
    
    // Funciones de utilidad
    getToken,
    hasPermission,
    hasRole,
    
    // Información adicional
    isAdmin: user?.role_name === 'Admin' || user?.role_name === 'Super Admin' || false,
    userName: user ? `${user.first_name} ${user.last_name}`.trim() : '',
    userEmail: user?.email || '',
    userId: user?.id || '',
    tenantId: user?.tenant_id || '',
  };
}

// Hook para proteger componentes
export function useRequireAuth(redirectTo: string = '/login') {
  const { isAuthenticated, isLoading } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push(redirectTo);
    }
  }, [isAuthenticated, isLoading, router, redirectTo]);

  return { isAuthenticated, isLoading };
}

// Hook para redirección si ya está autenticado
export function useRedirectIfAuthenticated(redirectTo: string = '/dashboard') {
  const { isAuthenticated, isLoading } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push(redirectTo);
    }
  }, [isAuthenticated, isLoading, router, redirectTo]);

  return { isAuthenticated, isLoading };
}