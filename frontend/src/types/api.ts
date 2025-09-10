// API Response Types for Proyecto Semilla

export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Article Types
export interface Article {
  id: string;
  tenant_id: string;
  title: string;
  slug: string;
  content: string;
  excerpt: string;
  author_id: string;
  category_id?: string;
  seo_title?: string;
  seo_description?: string;
  featured_image?: string;
  status: 'draft' | 'published' | 'review';
  is_featured: boolean;
  view_count: number;
  comment_count: number;
  like_count: number;
  tags: string[];
  published_at?: string;
  created_at: string;
  updated_at: string;
  author_name?: string;
  category_name?: string;
}

export interface ArticleCreate {
  title: string;
  slug: string;
  content: string;
  excerpt: string;
  category_id?: string;
  seo_title?: string;
  seo_description?: string;
  featured_image?: string;
  status: 'draft' | 'published' | 'review';
  is_featured: boolean;
  tags: string[];
}

export interface ArticleUpdate {
  title?: string;
  slug?: string;
  content?: string;
  excerpt?: string;
  category_id?: string;
  seo_title?: string;
  seo_description?: string;
  featured_image?: string;
  status?: 'draft' | 'published' | 'review';
  is_featured?: boolean;
  tags?: string[];
}

export interface ArticleStats {
  total_articles: number;
  published_articles: number;
  draft_articles: number;
  total_views: number;
  total_comments: number;
  total_likes: number;
}

// Category Types
export interface Category {
  id: string;
  tenant_id: string;
  name: string;
  slug: string;
  description?: string;
  color?: string;
  icon?: string;
  parent_id?: string;
  created_at: string;
  updated_at: string;
}

export interface CategoryCreate {
  name: string;
  slug: string;
  description?: string;
  color?: string;
  icon?: string;
  parent_id?: string;
}

export interface CategoryUpdate {
  name?: string;
  slug?: string;
  description?: string;
  color?: string;
  icon?: string;
  parent_id?: string;
}

// User Types
export interface User {
  id: string;
  tenant_id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  role_id: string;
  created_at: string;
  updated_at: string;
  role_name?: string;
}

export interface UserCreate {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  role_id: string;
}

export interface UserRegister {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  tenant_id: string;
}

export interface UserUpdate {
  email?: string;
  first_name?: string;
  last_name?: string;
  is_active?: boolean;
  role_id?: string;
}

// Tenant Types
export interface Tenant {
  id: string;
  name: string;
  slug: string;
  domain?: string;
  logo?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TenantCreate {
  name: string;
  slug: string;
  domain?: string;
  logo?: string;
}

export interface TenantUpdate {
  name?: string;
  slug?: string;
  domain?: string;
  logo?: string;
  is_active?: boolean;
}

// Role Types
export interface Role {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  permissions: string[];
  color: string;
  hierarchy_level: number;
  is_default: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RoleCreate {
  name: string;
  description?: string;
  permissions: string[];
  color?: string;
  hierarchy_level?: number;
  is_default?: boolean;
  is_active?: boolean;
}

export interface RoleUpdate {
  name?: string;
  description?: string;
  permissions?: string[];
  color?: string;
  hierarchy_level?: number;
  is_default?: boolean;
  is_active?: boolean;
}

export interface UserRoleAssignment {
  user_id: string;
  role_id: string;
}

export interface UserRoleResponse {
  user_id: string;
  role_id: string;
  role_name: string;
  assigned_at: string;
}

// Auth Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  token_type: string;
  expires_in: number;
  tenant_id: string;
  tenant_name: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface SwitchTenantResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  tenant_id: string;
  tenant_name: string;
}

// Health Check Types
export interface HealthCheckResponse {
  status: string;
  version: string;
  timestamp: string;
}

// Query Parameters
export interface ArticleQueryParams {
  skip?: number;
  limit?: number;
  status_filter?: 'draft' | 'published' | 'review';
  category_id?: string;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

// Error Types
export interface ApiError {
  detail: string;
  code?: string;
  field?: string;
  statusCode?: number;
}

// Generic API Error Response
export interface ErrorResponse {
  error: string;
  message: string;
  details?: any;
}

// Permission Constants
export const PERMISSIONS = {
  // User permissions
  USERS_READ: "users:read",
  USERS_WRITE: "users:write",
  USERS_DELETE: "users:delete",

  // Tenant permissions
  TENANTS_READ: "tenants:read",
  TENANTS_WRITE: "tenants:write",
  TENANTS_DELETE: "tenants:delete",

  // Article permissions
  ARTICLES_READ: "articles:read",
  ARTICLES_WRITE: "articles:write",
  ARTICLES_DELETE: "articles:delete",
  ARTICLES_PUBLISH: "articles:publish",

  // Role permissions
  ROLES_READ: "roles:read",
  ROLES_WRITE: "roles:write",
  ROLES_DELETE: "roles:delete",

  // Category permissions
  CATEGORIES_READ: "categories:read",
  CATEGORIES_WRITE: "categories:write",
  CATEGORIES_DELETE: "categories:delete",

  // Comment permissions
  COMMENTS_READ: "comments:read",
  COMMENTS_WRITE: "comments:write",
  COMMENTS_DELETE: "comments:delete",

  // System permissions
  SYSTEM_ADMIN: "system:admin",
  SYSTEM_CONFIG: "system:config"
} as const;

export type Permission = typeof PERMISSIONS[keyof typeof PERMISSIONS];

// Permission Groups for UI
export const PERMISSION_GROUPS = {
  users: {
    label: "Usuarios",
    permissions: [
      PERMISSIONS.USERS_READ,
      PERMISSIONS.USERS_WRITE,
      PERMISSIONS.USERS_DELETE
    ]
  },
  tenants: {
    label: "Tenants",
    permissions: [
      PERMISSIONS.TENANTS_READ,
      PERMISSIONS.TENANTS_WRITE,
      PERMISSIONS.TENANTS_DELETE
    ]
  },
  articles: {
    label: "Artículos",
    permissions: [
      PERMISSIONS.ARTICLES_READ,
      PERMISSIONS.ARTICLES_WRITE,
      PERMISSIONS.ARTICLES_DELETE,
      PERMISSIONS.ARTICLES_PUBLISH
    ]
  },
  roles: {
    label: "Roles",
    permissions: [
      PERMISSIONS.ROLES_READ,
      PERMISSIONS.ROLES_WRITE,
      PERMISSIONS.ROLES_DELETE
    ]
  },
  categories: {
    label: "Categorías",
    permissions: [
      PERMISSIONS.CATEGORIES_READ,
      PERMISSIONS.CATEGORIES_WRITE,
      PERMISSIONS.CATEGORIES_DELETE
    ]
  },
  comments: {
    label: "Comentarios",
    permissions: [
      PERMISSIONS.COMMENTS_READ,
      PERMISSIONS.COMMENTS_WRITE,
      PERMISSIONS.COMMENTS_DELETE
    ]
  },
  system: {
    label: "Sistema",
    permissions: [
      PERMISSIONS.SYSTEM_ADMIN,
      PERMISSIONS.SYSTEM_CONFIG
    ]
  }
} as const;

// Default Role Templates
export const DEFAULT_ROLES = {
  SUPER_ADMIN: {
    name: "Super Admin",
    description: "Control total del sistema",
    permissions: [
      PERMISSIONS.USERS_READ, PERMISSIONS.USERS_WRITE, PERMISSIONS.USERS_DELETE,
      PERMISSIONS.TENANTS_READ, PERMISSIONS.TENANTS_WRITE, PERMISSIONS.TENANTS_DELETE,
      PERMISSIONS.ARTICLES_READ, PERMISSIONS.ARTICLES_WRITE, PERMISSIONS.ARTICLES_DELETE, PERMISSIONS.ARTICLES_PUBLISH,
      PERMISSIONS.ROLES_READ, PERMISSIONS.ROLES_WRITE, PERMISSIONS.ROLES_DELETE,
      PERMISSIONS.CATEGORIES_READ, PERMISSIONS.CATEGORIES_WRITE, PERMISSIONS.CATEGORIES_DELETE,
      PERMISSIONS.COMMENTS_READ, PERMISSIONS.COMMENTS_WRITE, PERMISSIONS.COMMENTS_DELETE,
      PERMISSIONS.SYSTEM_ADMIN, PERMISSIONS.SYSTEM_CONFIG
    ],
    hierarchy_level: 1000,
    color: "#FF0000"
  },
  ADMIN: {
    name: "Admin",
    description: "Administración de tenant",
    permissions: [
      PERMISSIONS.USERS_READ, PERMISSIONS.USERS_WRITE, PERMISSIONS.USERS_DELETE,
      PERMISSIONS.TENANTS_READ, PERMISSIONS.TENANTS_WRITE,
      PERMISSIONS.ARTICLES_READ, PERMISSIONS.ARTICLES_WRITE, PERMISSIONS.ARTICLES_DELETE, PERMISSIONS.ARTICLES_PUBLISH,
      PERMISSIONS.ROLES_READ, PERMISSIONS.ROLES_WRITE, PERMISSIONS.ROLES_DELETE,
      PERMISSIONS.CATEGORIES_READ, PERMISSIONS.CATEGORIES_WRITE, PERMISSIONS.CATEGORIES_DELETE,
      PERMISSIONS.COMMENTS_READ, PERMISSIONS.COMMENTS_WRITE, PERMISSIONS.COMMENTS_DELETE,
      PERMISSIONS.SYSTEM_CONFIG
    ],
    hierarchy_level: 500,
    color: "#FF6B35"
  },
  MANAGER: {
    name: "Manager",
    description: "Gestión de contenido y usuarios",
    permissions: [
      PERMISSIONS.USERS_READ, PERMISSIONS.USERS_WRITE,
      PERMISSIONS.ARTICLES_READ, PERMISSIONS.ARTICLES_WRITE, PERMISSIONS.ARTICLES_DELETE, PERMISSIONS.ARTICLES_PUBLISH,
      PERMISSIONS.CATEGORIES_READ, PERMISSIONS.CATEGORIES_WRITE, PERMISSIONS.CATEGORIES_DELETE,
      PERMISSIONS.COMMENTS_READ, PERMISSIONS.COMMENTS_WRITE, PERMISSIONS.COMMENTS_DELETE
    ],
    hierarchy_level: 300,
    color: "#4ECDC4"
  },
  EDITOR: {
    name: "Editor",
    description: "Creación y edición de contenido",
    permissions: [
      PERMISSIONS.ARTICLES_READ, PERMISSIONS.ARTICLES_WRITE, PERMISSIONS.ARTICLES_PUBLISH,
      PERMISSIONS.CATEGORIES_READ,
      PERMISSIONS.COMMENTS_READ, PERMISSIONS.COMMENTS_WRITE
    ],
    hierarchy_level: 200,
    color: "#45B7D1"
  },
  USER: {
    name: "User",
    description: "Usuario básico con permisos limitados",
    permissions: [
      PERMISSIONS.USERS_READ,
      PERMISSIONS.ARTICLES_READ,
      PERMISSIONS.CATEGORIES_READ,
      PERMISSIONS.COMMENTS_READ, PERMISSIONS.COMMENTS_WRITE
    ],
    hierarchy_level: 100,
    color: "#96CEB4"
  }
} as const;