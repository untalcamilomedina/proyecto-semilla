import { useState, useEffect, useCallback } from 'react';
import { Permission, PERMISSIONS } from '@/types/api';

interface UsePermissionsReturn {
  userPermissions: string[];
  hasPermission: (permission: Permission) => boolean;
  hasAnyPermission: (permissions: Permission[]) => boolean;
  hasAllPermissions: (permissions: Permission[]) => boolean;
  canAccess: (requiredPermissions: Permission | Permission[], requireAll?: boolean) => boolean;
  isLoading: boolean;
  error: string | null;
  refreshPermissions: () => Promise<void>;
}

// Mock user permissions for development - replace with actual user data
const MOCK_USER_PERMISSIONS = [
  PERMISSIONS.USERS_READ,
  PERMISSIONS.ARTICLES_READ,
  PERMISSIONS.ARTICLES_WRITE,
  PERMISSIONS.CATEGORIES_READ,
  PERMISSIONS.COMMENTS_READ,
  PERMISSIONS.COMMENTS_WRITE,
  PERMISSIONS.ROLES_READ
];

export function usePermissions(): UsePermissionsReturn {
  const [userPermissions, setUserPermissions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadPermissions = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // TODO: Replace with actual API call to get user permissions
      // For now, using mock data
      setUserPermissions(MOCK_USER_PERMISSIONS);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load permissions');
      console.error('Error loading permissions:', err);
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