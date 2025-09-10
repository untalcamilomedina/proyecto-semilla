import { useState, useEffect, useCallback } from 'react';
import { Permission, PERMISSIONS } from '../types/api';
import { apiClient } from '../lib/api-client';

/**
 * Hook personalizado para gestionar permisos de usuario
 *
 * Proporciona funcionalidades para:
 * - Obtener permisos del usuario desde la API
 * - Verificar permisos individuales
 * - Verificar múltiples permisos (AND/OR)
 * - Control de acceso basado en permisos
 * - Cache y refresh automático de permisos
 *
 * @returns Objeto con estado de permisos y funciones de verificación
 */
interface UsePermissionsReturn {
  /** Lista de permisos del usuario actual */
  userPermissions: string[];
  /** Verifica si el usuario tiene un permiso específico */
  hasPermission: (permission: Permission) => boolean;
  /** Verifica si el usuario tiene al menos uno de los permisos especificados */
  hasAnyPermission: (permissions: Permission[]) => boolean;
  /** Verifica si el usuario tiene todos los permisos especificados */
  hasAllPermissions: (permissions: Permission[]) => boolean;
  /** Verifica acceso basado en permisos con opción AND/OR */
  canAccess: (requiredPermissions: Permission | Permission[], requireAll?: boolean) => boolean;
  /** Indica si se están cargando los permisos */
  isLoading: boolean;
  /** Error ocurrido al cargar permisos */
  error: string | null;
  /** Función para refrescar permisos desde la API */
  refreshPermissions: () => Promise<void>;
}

// Default permissions when API is not available
const DEFAULT_PERMISSIONS: string[] = [];

/**
 * Hook principal para gestión de permisos de usuario
 *
 * Carga automáticamente los permisos del usuario al montar el componente
 * y proporciona funciones para verificar permisos de manera eficiente.
 *
 * @returns {UsePermissionsReturn} Objeto con estado y funciones de permisos
 *
 * @example
 * ```typescript
 * const { hasPermission, canAccess, isLoading } = usePermissions();
 *
 * if (isLoading) return <LoadingSpinner />;
 *
 * if (!hasPermission(PERMISSIONS.ARTICLES_WRITE)) {
 *   return <AccessDenied />;
 * }
 *
 * return <EditArticleForm />;
 * ```
 */
export function usePermissions(): UsePermissionsReturn {
  const [userPermissions, setUserPermissions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadPermissions = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Get user permissions from API
      const response = await apiClient.getUserPermissions();
      setUserPermissions(response.permissions || DEFAULT_PERMISSIONS);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load permissions');
      console.error('Error loading permissions:', err);
      // Set default permissions on error
      setUserPermissions(DEFAULT_PERMISSIONS);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refreshPermissions = useCallback(async () => {
    await loadPermissions();
  }, [loadPermissions]);

  useEffect(() => {
    loadPermissions();
  }, [loadPermissions]);

  const hasPermission = useCallback((permission: Permission): boolean => {
    return userPermissions.includes(permission);
  }, [userPermissions]);

  const hasAnyPermission = useCallback((permissions: Permission[]): boolean => {
    return permissions.some(permission => userPermissions.includes(permission));
  }, [userPermissions]);

  const hasAllPermissions = useCallback((permissions: Permission[]): boolean => {
    return permissions.every(permission => userPermissions.includes(permission));
  }, [userPermissions]);

  const canAccess = useCallback((
    requiredPermissions: Permission | Permission[],
    requireAll: boolean = false
  ): boolean => {
    const permissions = Array.isArray(requiredPermissions)
      ? requiredPermissions
      : [requiredPermissions];

    return requireAll
      ? hasAllPermissions(permissions)
      : hasAnyPermission(permissions);
  }, [hasAllPermissions, hasAnyPermission]);

  return {
    userPermissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    canAccess,
    isLoading,
    error,
    refreshPermissions
  };
}

// Hook for checking specific permissions with memoization
export function usePermissionCheck() {
  const { hasPermission, hasAnyPermission, hasAllPermissions, canAccess } = usePermissions();

  return {
    // User management permissions
    canReadUsers: () => hasPermission(PERMISSIONS.USERS_READ),
    canWriteUsers: () => hasPermission(PERMISSIONS.USERS_WRITE),
    canDeleteUsers: () => hasPermission(PERMISSIONS.USERS_DELETE),
    canManageUsers: () => hasAnyPermission([PERMISSIONS.USERS_WRITE, PERMISSIONS.USERS_DELETE]),

    // Article permissions
    canReadArticles: () => hasPermission(PERMISSIONS.ARTICLES_READ),
    canWriteArticles: () => hasPermission(PERMISSIONS.ARTICLES_WRITE),
    canDeleteArticles: () => hasPermission(PERMISSIONS.ARTICLES_DELETE),
    canPublishArticles: () => hasPermission(PERMISSIONS.ARTICLES_PUBLISH),
    canManageArticles: () => hasAnyPermission([
      PERMISSIONS.ARTICLES_WRITE,
      PERMISSIONS.ARTICLES_DELETE,
      PERMISSIONS.ARTICLES_PUBLISH
    ]),

    // Role permissions
    canReadRoles: () => hasPermission(PERMISSIONS.ROLES_READ),
    canWriteRoles: () => hasPermission(PERMISSIONS.ROLES_WRITE),
    canDeleteRoles: () => hasPermission(PERMISSIONS.ROLES_DELETE),
    canManageRoles: () => hasAnyPermission([PERMISSIONS.ROLES_WRITE, PERMISSIONS.ROLES_DELETE]),

    // Tenant permissions
    canReadTenants: () => hasPermission(PERMISSIONS.TENANTS_READ),
    canWriteTenants: () => hasPermission(PERMISSIONS.TENANTS_WRITE),
    canDeleteTenants: () => hasPermission(PERMISSIONS.TENANTS_DELETE),
    canManageTenants: () => hasAnyPermission([PERMISSIONS.TENANTS_WRITE, PERMISSIONS.TENANTS_DELETE]),

    // Category permissions
    canReadCategories: () => hasPermission(PERMISSIONS.CATEGORIES_READ),
    canWriteCategories: () => hasPermission(PERMISSIONS.CATEGORIES_WRITE),
    canDeleteCategories: () => hasPermission(PERMISSIONS.CATEGORIES_DELETE),
    canManageCategories: () => hasAnyPermission([PERMISSIONS.CATEGORIES_WRITE, PERMISSIONS.CATEGORIES_DELETE]),

    // Comment permissions
    canReadComments: () => hasPermission(PERMISSIONS.COMMENTS_READ),
    canWriteComments: () => hasPermission(PERMISSIONS.COMMENTS_WRITE),
    canDeleteComments: () => hasPermission(PERMISSIONS.COMMENTS_DELETE),
    canManageComments: () => hasAnyPermission([PERMISSIONS.COMMENTS_WRITE, PERMISSIONS.COMMENTS_DELETE]),

    // System permissions
    isSystemAdmin: () => hasPermission(PERMISSIONS.SYSTEM_ADMIN),
    canConfigureSystem: () => hasPermission(PERMISSIONS.SYSTEM_CONFIG),

    // Generic access check
    canAccess
  };
}

// Utility functions for permission checking
export const PermissionUtils = {
  hasPermission: (userPermissions: string[], permission: Permission): boolean => {
    return userPermissions.includes(permission);
  },

  hasAnyPermission: (userPermissions: string[], permissions: Permission[]): boolean => {
    return permissions.some(permission => userPermissions.includes(permission));
  },

  hasAllPermissions: (userPermissions: string[], permissions: Permission[]): boolean => {
    return permissions.every(permission => userPermissions.includes(permission));
  },

  canAccess: (
    userPermissions: string[],
    requiredPermissions: Permission | Permission[],
    requireAll: boolean = false
  ): boolean => {
    const permissions = Array.isArray(requiredPermissions)
      ? requiredPermissions
      : [requiredPermissions];

    return requireAll
      ? PermissionUtils.hasAllPermissions(userPermissions, permissions)
      : PermissionUtils.hasAnyPermission(userPermissions, permissions);
  }
};