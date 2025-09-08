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
  is_system: boolean;
  created_at: string;
  updated_at: string;
}

export interface RoleCreate {
  name: string;
  description?: string;
  permissions: string[];
}

export interface RoleUpdate {
  name?: string;
  description?: string;
  permissions?: string[];
}

// Auth Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
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
}

// Generic API Error Response
export interface ErrorResponse {
  error: string;
  message: string;
  details?: any;
}