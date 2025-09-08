import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../lib/api-client';
import {
  Article,
  ArticleCreate,
  ArticleUpdate,
  ArticleQueryParams,
  Category,
  CategoryCreate,
  CategoryUpdate,
  User,
  UserCreate,
  UserUpdate,
  Tenant,
  TenantCreate,
  TenantUpdate,
  Role,
  RoleCreate,
  RoleUpdate,
  ArticleStats,
  LoginRequest,
  UserRegister
} from '../types/api';
import { useUIStore } from '../stores';

// Query Keys
export const queryKeys = {
  articles: ['articles'] as const,
  article: (id: string) => ['articles', id] as const,
  articleStats: ['articles', 'stats'] as const,

  categories: ['categories'] as const,
  category: (id: string) => ['categories', id] as const,
  categoryStats: ['categories', 'stats'] as const,

  users: ['users'] as const,
  user: (id: string) => ['users', id] as const,

  tenants: ['tenants'] as const,
  tenant: (id: string) => ['tenants', id] as const,
  userTenants: ['tenants', 'user'] as const,

  roles: ['roles'] as const,
  role: (id: string) => ['roles', id] as const,

  health: ['health'] as const,
};

// Articles Hooks
export function useArticles(params?: ArticleQueryParams) {
  return useQuery({
    queryKey: [...queryKeys.articles, params],
    queryFn: () => apiClient.getArticles(params),
  });
}

export function useArticle(id: string) {
  return useQuery({
    queryKey: queryKeys.article(id),
    queryFn: () => apiClient.getArticle(id),
    enabled: !!id,
  });
}

export function useArticleStats() {
  return useQuery({
    queryKey: queryKeys.articleStats,
    queryFn: () => apiClient.getArticleStats(),
  });
}

export function useCreateArticle() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: (article: ArticleCreate) => apiClient.createArticle(article),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.articles });
      addNotification({
        type: 'success',
        title: 'Artículo creado',
        message: `El artículo "${data.title}" ha sido creado exitosamente.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al crear artículo',
        message: error.detail || 'Ha ocurrido un error al crear el artículo.',
      });
    },
  });
}

export function useUpdateArticle() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: ({ id, article }: { id: string; article: ArticleUpdate }) =>
      apiClient.updateArticle(id, article),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.articles });
      queryClient.invalidateQueries({ queryKey: queryKeys.article(data.id) });
      addNotification({
        type: 'success',
        title: 'Artículo actualizado',
        message: `El artículo "${data.title}" ha sido actualizado exitosamente.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al actualizar artículo',
        message: error.detail || 'Ha ocurrido un error al actualizar el artículo.',
      });
    },
  });
}

export function useDeleteArticle() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: (id: string) => apiClient.deleteArticle(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.articles });
      addNotification({
        type: 'success',
        title: 'Artículo eliminado',
        message: 'El artículo ha sido eliminado exitosamente.',
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al eliminar artículo',
        message: error.detail || 'Ha ocurrido un error al eliminar el artículo.',
      });
    },
  });
}

// Categories Hooks
export function useCategories() {
  return useQuery({
    queryKey: queryKeys.categories,
    queryFn: () => apiClient.getCategories(),
  });
}

export function useCategory(id: string) {
  return useQuery({
    queryKey: queryKeys.category(id),
    queryFn: () => apiClient.getCategory(id),
    enabled: !!id,
  });
}

export function useCategoryStats() {
  return useQuery({
    queryKey: queryKeys.categoryStats,
    queryFn: () => apiClient.getCategoryStats(),
  });
}

export function useCreateCategory() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: (category: CategoryCreate) => apiClient.createCategory(category),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.categories });
      addNotification({
        type: 'success',
        title: 'Categoría creada',
        message: `La categoría "${data.name}" ha sido creada exitosamente.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al crear categoría',
        message: error.detail || 'Ha ocurrido un error al crear la categoría.',
      });
    },
  });
}

export function useUpdateCategory() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: ({ id, category }: { id: string; category: CategoryUpdate }) =>
      apiClient.updateCategory(id, category),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.categories });
      queryClient.invalidateQueries({ queryKey: queryKeys.category(data.id) });
      addNotification({
        type: 'success',
        title: 'Categoría actualizada',
        message: `La categoría "${data.name}" ha sido actualizada exitosamente.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al actualizar categoría',
        message: error.detail || 'Ha ocurrido un error al actualizar la categoría.',
      });
    },
  });
}

export function useDeleteCategory() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: (id: string) => apiClient.deleteCategory(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.categories });
      addNotification({
        type: 'success',
        title: 'Categoría eliminada',
        message: 'La categoría ha sido eliminada exitosamente.',
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al eliminar categoría',
        message: error.detail || 'Ha ocurrido un error al eliminar la categoría.',
      });
    },
  });
}

// Users Hooks
export function useUsers() {
  return useQuery({
    queryKey: queryKeys.users,
    queryFn: () => apiClient.getUsers(),
  });
}

export function useUser(id: string) {
  return useQuery({
    queryKey: queryKeys.user(id),
    queryFn: () => apiClient.getUser(id),
    enabled: !!id,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: (user: UserCreate) => apiClient.createUser(user),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users });
      addNotification({
        type: 'success',
        title: 'Usuario creado',
        message: `El usuario "${data.email}" ha sido creado exitosamente.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al crear usuario',
        message: error.detail || 'Ha ocurrido un error al crear el usuario.',
      });
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: ({ id, user }: { id: string; user: UserUpdate }) =>
      apiClient.updateUser(id, user),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users });
      queryClient.invalidateQueries({ queryKey: queryKeys.user(data.id) });
      addNotification({
        type: 'success',
        title: 'Usuario actualizado',
        message: `El usuario "${data.email}" ha sido actualizado exitosamente.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al actualizar usuario',
        message: error.detail || 'Ha ocurrido un error al actualizar el usuario.',
      });
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: (id: string) => apiClient.deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users });
      addNotification({
        type: 'success',
        title: 'Usuario eliminado',
        message: 'El usuario ha sido eliminado exitosamente.',
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al eliminar usuario',
        message: error.detail || 'Ha ocurrido un error al eliminar el usuario.',
      });
    },
  });
}

// Tenants Hooks
export function useTenants() {
  return useQuery({
    queryKey: queryKeys.tenants,
    queryFn: () => apiClient.getTenants(),
  });
}

export function useTenant(id: string) {
  return useQuery({
    queryKey: queryKeys.tenant(id),
    queryFn: () => apiClient.getTenant(id),
    enabled: !!id,
  });
}

export function useUserTenants() {
  return useQuery({
    queryKey: queryKeys.userTenants,
    queryFn: () => apiClient.getUserTenants(),
  });
}

export function useCreateTenant() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: (tenant: TenantCreate) => apiClient.createTenant(tenant),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tenants });
      addNotification({
        type: 'success',
        title: 'Tenant creado',
        message: `El tenant "${data.name}" ha sido creado exitosamente.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al crear tenant',
        message: error.detail || 'Ha ocurrido un error al crear el tenant.',
      });
    },
  });
}

export function useUpdateTenant() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: ({ id, tenant }: { id: string; tenant: TenantUpdate }) =>
      apiClient.updateTenant(id, tenant),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tenants });
      queryClient.invalidateQueries({ queryKey: queryKeys.tenant(data.id) });
      addNotification({
        type: 'success',
        title: 'Tenant actualizado',
        message: `El tenant "${data.name}" ha sido actualizado exitosamente.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al actualizar tenant',
        message: error.detail || 'Ha ocurrido un error al actualizar el tenant.',
      });
    },
  });
}

export function useDeleteTenant() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: (id: string) => apiClient.deleteTenant(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tenants });
      addNotification({
        type: 'success',
        title: 'Tenant eliminado',
        message: 'El tenant ha sido eliminado exitosamente.',
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al eliminar tenant',
        message: error.detail || 'Ha ocurrido un error al eliminar el tenant.',
      });
    },
  });
}

export function useSwitchTenant() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: (tenantId: string) => apiClient.switchTenant(tenantId),
    onSuccess: (data) => {
      // Clear all cached data when switching tenants
      queryClient.clear();
      addNotification({
        type: 'success',
        title: 'Tenant cambiado',
        message: `Se ha cambiado al tenant "${data.tenant_name}".`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al cambiar tenant',
        message: error.detail || 'Ha ocurrido un error al cambiar de tenant.',
      });
    },
  });
}

// Roles Hooks
export function useRoles() {
  return useQuery({
    queryKey: queryKeys.roles,
    queryFn: () => apiClient.getRoles(),
  });
}

export function useRole(id: string) {
  return useQuery({
    queryKey: queryKeys.role(id),
    queryFn: () => apiClient.getRole(id),
    enabled: !!id,
  });
}

export function useCreateRole() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: (role: RoleCreate) => apiClient.createRole(role),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.roles });
      addNotification({
        type: 'success',
        title: 'Rol creado',
        message: `El rol "${data.name}" ha sido creado exitosamente.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al crear rol',
        message: error.detail || 'Ha ocurrido un error al crear el rol.',
      });
    },
  });
}

export function useUpdateRole() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: ({ id, role }: { id: string; role: RoleUpdate }) =>
      apiClient.updateRole(id, role),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.roles });
      queryClient.invalidateQueries({ queryKey: queryKeys.role(data.id) });
      addNotification({
        type: 'success',
        title: 'Rol actualizado',
        message: `El rol "${data.name}" ha sido actualizado exitosamente.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al actualizar rol',
        message: error.detail || 'Ha ocurrido un error al actualizar el rol.',
      });
    },
  });
}

export function useDeleteRole() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: (id: string) => apiClient.deleteRole(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.roles });
      addNotification({
        type: 'success',
        title: 'Rol eliminado',
        message: 'El rol ha sido eliminado exitosamente.',
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al eliminar rol',
        message: error.detail || 'Ha ocurrido un error al eliminar el rol.',
      });
    },
  });
}

export function useAssignRoleToUser() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: ({ userId, roleId }: { userId: string; roleId: string }) =>
      apiClient.assignRoleToUser(userId, roleId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users });
      queryClient.invalidateQueries({ queryKey: queryKeys.user(data.user_id) });
      addNotification({
        type: 'success',
        title: 'Rol asignado',
        message: `El rol "${data.role_name}" ha sido asignado exitosamente.`,
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al asignar rol',
        message: error.detail || 'Ha ocurrido un error al asignar el rol.',
      });
    },
  });
}

export function useRemoveRoleFromUser() {
  const queryClient = useQueryClient();
  const { addNotification } = useUIStore();

  return useMutation({
    mutationFn: ({ userId, roleId }: { userId: string; roleId: string }) =>
      apiClient.removeRoleFromUser(userId, roleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users });
      addNotification({
        type: 'success',
        title: 'Rol removido',
        message: 'El rol ha sido removido exitosamente.',
      });
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error al remover rol',
        message: error.detail || 'Ha ocurrido un error al remover el rol.',
      });
    },
  });
}

// Health Check Hook
export function useHealthCheck() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useDetailedHealthCheck() {
  return useQuery({
    queryKey: [...queryKeys.health, 'detailed'],
    queryFn: () => apiClient.detailedHealthCheck(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}