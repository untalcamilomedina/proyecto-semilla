/**
 * CMS API hooks using TanStack Query.
 * Provides data fetching, caching, and mutations for CMS content.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, apiGet, apiPost, apiPatch, apiDelete } from '@/lib/api';

// ── Types ──────────────────────────────────────────────────

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  parent: number | null;
  position: number;
}

export interface ContentPage {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  body_mdx?: string;
  status: 'draft' | 'published' | 'archived';
  is_featured: boolean;
  author: number | null;
  author_email?: string;
  category: number | null;
  category_name?: string;
  seo_title: string;
  seo_description?: string;
  og_image_url?: string;
  frontmatter: Record<string, unknown>;
  tags: string[];
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface MediaAsset {
  id: number;
  filename: string;
  file: string;
  mime_type: string;
  size_bytes: number;
  alt_text: string;
  uploaded_by: number | null;
  created_at: string;
}

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ── Query Keys ─────────────────────────────────────────────

export const cmsKeys = {
  all: ['cms'] as const,
  pages: () => [...cmsKeys.all, 'pages'] as const,
  page: (id: number) => [...cmsKeys.pages(), id] as const,
  pageBySlug: (slug: string) => [...cmsKeys.pages(), 'slug', slug] as const,
  categories: () => [...cmsKeys.all, 'categories'] as const,
  media: () => [...cmsKeys.all, 'media'] as const,
};

// ── Pages ──────────────────────────────────────────────────

export function useContentPages(params?: { status?: string; category?: number }) {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set('status', params.status);
  if (params?.category) searchParams.set('category', String(params.category));
  const qs = searchParams.toString();

  return useQuery({
    queryKey: [...cmsKeys.pages(), params],
    queryFn: () => apiGet<PaginatedResponse<ContentPage>>(
      `/api/v1/cms/pages/${qs ? `?${qs}` : ''}`
    ),
  });
}

export function useContentPage(id: number) {
  return useQuery({
    queryKey: cmsKeys.page(id),
    queryFn: () => apiGet<ContentPage>(`/api/v1/cms/pages/${id}/`),
    enabled: !!id,
  });
}

export function useCreatePage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<ContentPage>) =>
      apiPost<ContentPage>('/api/v1/cms/pages/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cmsKeys.pages() });
    },
  });
}

export function useUpdatePage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }: Partial<ContentPage> & { id: number }) =>
      apiPatch<ContentPage>(`/api/v1/cms/pages/${id}/`, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: cmsKeys.page(variables.id) });
      queryClient.invalidateQueries({ queryKey: cmsKeys.pages() });
    },
  });
}

export function useDeletePage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => apiDelete(`/api/v1/cms/pages/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cmsKeys.pages() });
    },
  });
}

// ── Categories ─────────────────────────────────────────────

export function useCategories() {
  return useQuery({
    queryKey: cmsKeys.categories(),
    queryFn: () => apiGet<PaginatedResponse<Category>>('/api/v1/cms/categories/'),
  });
}

export function useCreateCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Category>) =>
      apiPost<Category>('/api/v1/cms/categories/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cmsKeys.categories() });
    },
  });
}

// ── Media ──────────────────────────────────────────────────

export function useMediaAssets() {
  return useQuery({
    queryKey: cmsKeys.media(),
    queryFn: () => apiGet<PaginatedResponse<MediaAsset>>('/api/v1/cms/media/'),
  });
}

export function useUploadMedia() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('alt_text', file.name);
      return api<MediaAsset>('/api/v1/cms/media/', {
        method: 'POST',
        body: formData,
        headers: {},  // Let browser set Content-Type with boundary
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cmsKeys.media() });
    },
  });
}
