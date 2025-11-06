import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  User,
  UserRegister,
  UserCreate,
  UserUpdate,
  Article,
  ArticleCreate,
  ArticleUpdate,
  ArticleQueryParams,
  ArticleStats,
  Tenant,
  TenantCreate,
  TenantUpdate,
  Role,
  RoleCreate,
  RoleUpdate,
  Category,
  CategoryCreate,
  CategoryUpdate,
  LoginResponse,
  SwitchTenantResponse,
  UserRoleResponse
} from '../types/api';


class ApiClient {
  private axiosInstance: AxiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7777',
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.axiosInstance.interceptors.request.use(
      (config) => {
        // With `withCredentials: true`, the browser automatically handles sending
        // the HttpOnly session cookie. Manually setting the Authorization header
        // from localStorage or a readable cookie conflicts with this mechanism
        // and is the likely source of the authentication issue.
        // We remove this manual logic to rely solely on the browser's
        // cookie handling.
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle errors
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login
          console.error('Unauthorized access - redirecting to login');
          
          // Clear auth data
          if (typeof window !== 'undefined') {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            
            // Clear cookies
            document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
            
            // Only redirect if not already on login or register page
            const currentPath = window.location.pathname;
            if (!currentPath.includes('/login') && !currentPath.includes('/register')) {
              window.location.href = '/login';
            }
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  // Generic GET method
  async get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
    const response: AxiosResponse<T> = await this.axiosInstance.get(url, { params });
    return response.data;
  }

  // Authentication methods

  async register(data: UserRegister): Promise<User> {
    const response: AxiosResponse<User> = await this.axiosInstance.post('/api/v1/auth/register', data);
    return response.data;
  }

  async login(data: FormData): Promise<LoginResponse> {
    const response = await this.axiosInstance.post('/api/v1/auth/login', data, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  }

  async logout(): Promise<void> {
    await this.axiosInstance.post('/api/v1/auth/logout');
  }

  async logoutAll(): Promise<void> {
    await this.axiosInstance.post('/api/v1/auth/logout-all');
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.axiosInstance.get('/api/v1/auth/me');
    return response.data;
  }

  // Article methods
  async getArticles(params?: ArticleQueryParams): Promise<{ articles: Article[], total: number }> {
    const response: AxiosResponse<{ articles: Article[], total: number }> = await this.axiosInstance.get('/api/v1/articles', { params });
    return response.data;
  }

  async getArticle(id: string): Promise<Article> {
    const response: AxiosResponse<Article> = await this.axiosInstance.get(`/api/v1/articles/${id}`);
    return response.data;
  }

  async createArticle(article: ArticleCreate): Promise<Article> {
    const response: AxiosResponse<Article> = await this.axiosInstance.post('/api/v1/articles', article);
    return response.data;
  }

  async updateArticle(id: string, article: ArticleUpdate): Promise<Article> {
    const response: AxiosResponse<Article> = await this.axiosInstance.put(`/api/v1/articles/${id}`, article);
    return response.data;
  }

  async deleteArticle(id: string): Promise<void> {
    await this.axiosInstance.delete(`/api/v1/articles/${id}`);
  }

  async getArticleStats(): Promise<ArticleStats> {
    const response: AxiosResponse<ArticleStats> = await this.axiosInstance.get('/api/v1/articles/stats');
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    const response: AxiosResponse<{ status: string; service: string; version: string }> =
      await this.axiosInstance.get('/api/v1/health');
    return response.data;
  }

  async detailedHealthCheck(): Promise<any> {
    const response: AxiosResponse<any> = await this.axiosInstance.get('/api/v1/health/detailed');
    return response.data;
  }

  // Placeholder methods for other entities (to be implemented as needed)
  async getUsers(): Promise<User[]> {
    const response: AxiosResponse<User[]> = await this.axiosInstance.get('/api/v1/users');
    return response.data;
  }

  async getUser(id: string): Promise<User> {
    const response: AxiosResponse<User> = await this.axiosInstance.get(`/api/v1/users/${id}`);
    return response.data;
  }

  async createUser(user: UserCreate): Promise<User> {
    const response: AxiosResponse<User> = await this.axiosInstance.post('/api/v1/users', user);
    return response.data;
  }

  async updateUser(id: string, user: UserUpdate): Promise<User> {
    const response: AxiosResponse<User> = await this.axiosInstance.put(`/api/v1/users/${id}`, user);
    return response.data;
  }

  async deleteUser(id: string): Promise<void> {
    await this.axiosInstance.delete(`/api/v1/users/${id}`);
  }

  // Tenants
  async getTenants(): Promise<Tenant[]> {
    const response: AxiosResponse<Tenant[]> = await this.axiosInstance.get('/api/v1/tenants');
    return response.data;
  }

  async getTenant(id: string): Promise<Tenant> {
    const response: AxiosResponse<Tenant> = await this.axiosInstance.get(`/api/v1/tenants/${id}`);
    return response.data;
  }

  async getUserTenants(): Promise<Tenant[]> {
    const response: AxiosResponse<Tenant[]> = await this.axiosInstance.get('/api/v1/tenants/user-tenants');
    return response.data;
  }

  async createTenant(tenant: TenantCreate): Promise<Tenant> {
    const response: AxiosResponse<Tenant> = await this.axiosInstance.post('/api/v1/tenants', tenant);
    return response.data;
  }

  async updateTenant(id: string, tenant: TenantUpdate): Promise<Tenant> {
    const response: AxiosResponse<Tenant> = await this.axiosInstance.put(`/api/v1/tenants/${id}`, tenant);
    return response.data;
  }

  async deleteTenant(id: string): Promise<void> {
    await this.axiosInstance.delete(`/api/v1/tenants/${id}`);
  }

  async switchTenant(tenantId: string): Promise<SwitchTenantResponse> {
    const response: AxiosResponse<SwitchTenantResponse> = await this.axiosInstance.post(`/api/v1/auth/switch-tenant/${tenantId}`);
    return response.data;
  }

  // Roles
  async getRoles(): Promise<Role[]> {
    const response: AxiosResponse<Role[]> = await this.axiosInstance.get('/api/v1/roles');
    return response.data;
  }

  async getRole(id: string): Promise<Role> {
    const response: AxiosResponse<Role> = await this.axiosInstance.get(`/api/v1/roles/${id}`);
    return response.data;
  }

  async createRole(role: RoleCreate): Promise<Role> {
    const response: AxiosResponse<Role> = await this.axiosInstance.post('/api/v1/roles', role);
    return response.data;
  }

  async updateRole(id: string, role: RoleUpdate): Promise<Role> {
    const response: AxiosResponse<Role> = await this.axiosInstance.put(`/api/v1/roles/${id}`, role);
    return response.data;
  }

  async deleteRole(id: string): Promise<void> {
    await this.axiosInstance.delete(`/api/v1/roles/${id}`);
  }

  async assignRoleToUser(userId: string, roleId: string): Promise<UserRoleResponse> {
    const response: AxiosResponse<UserRoleResponse> = await this.axiosInstance.post(`/api/v1/users/${userId}/roles/${roleId}`);
    return response.data;
  }

  async removeRoleFromUser(userId: string, roleId: string): Promise<void> {
    await this.axiosInstance.delete(`/api/v1/users/${userId}/roles/${roleId}`);
  }

  // Categories (placeholders)
  async getCategories(): Promise<Category[]> {
    const response: AxiosResponse<Category[]> = await this.axiosInstance.get('/api/v1/categories');
    return response.data;
  }

  async getCategory(id: string): Promise<Category> {
    const response: AxiosResponse<Category> = await this.axiosInstance.get(`/api/v1/categories/${id}`);
    return response.data;
  }

  async createCategory(category: CategoryCreate): Promise<Category> {
    const response: AxiosResponse<Category> = await this.axiosInstance.post('/api/v1/categories', category);
    return response.data;
  }

  async updateCategory(id: string, category: CategoryUpdate): Promise<Category> {
    const response: AxiosResponse<Category> = await this.axiosInstance.put(`/api/v1/categories/${id}`, category);
    return response.data;
  }

  async deleteCategory(id: string): Promise<void> {
    await this.axiosInstance.delete(`/api/v1/categories/${id}`);
  }

  async getCategoryStats(): Promise<Record<string, unknown>> {
    const response: AxiosResponse<Record<string, unknown>> = await this.axiosInstance.get('/api/v1/categories/stats');
    return response.data;
  }

  // User permissions
  async getUserPermissions(): Promise<{ permissions: string[] }> {
    const response: AxiosResponse<{ permissions: string[] }> = await this.axiosInstance.get('/api/v1/auth/permissions');
    return response.data;
  }

  // Setup status
  async getSetupStatus(): Promise<{ needs_setup: boolean; user_count: number; message: string }> {
    const response: AxiosResponse<{ needs_setup: boolean; user_count: number; message: string }> =
      await this.axiosInstance.get('/api/v1/auth/setup-status');
    return response.data;
  }

  // Setup wizard endpoints
  async checkSystemRequirements(): Promise<any> {
    const response = await this.axiosInstance.get('/api/v1/setup/check-requirements');
    return response.data;
  }

  async generateSecrets(): Promise<any> {
    const response = await this.axiosInstance.post('/api/v1/setup/generate-secrets');
    return response.data;
  }

  async configureSystem(config: any): Promise<any> {
    const response = await this.axiosInstance.post('/api/v1/setup/configure', config);
    return response.data;
  }

  async checkProductionReadiness(): Promise<any> {
    const response = await this.axiosInstance.get('/api/v1/setup/production-readiness');
    return response.data;
  }

  async getSetupWizardStatus(): Promise<any> {
    const response = await this.axiosInstance.get('/api/v1/setup/status');
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();