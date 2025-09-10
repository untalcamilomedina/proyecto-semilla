import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../lib/api-client';
import { useAuth } from '../components/providers';
import {
  Article,
  ArticleCreate,
  ArticleUpdate,
  ArticleStats,
  ArticleQueryParams,
  ApiError
} from '../types/api';

// Query keys
export const articleKeys = {
  all: ['articles'] as const,
  lists: () => [...articleKeys.all, 'list'] as const,
  list: (params: ArticleQueryParams) => [...articleKeys.lists(), params] as const,
  details: () => [...articleKeys.all, 'detail'] as const,
  detail: (id: string) => [...articleKeys.details(), id] as const,
  stats: () => [...articleKeys.all, 'stats'] as const,
};

// Get articles hook
export const useArticles = (params?: ArticleQueryParams) => {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: articleKeys.list(params || {}),
    queryFn: () => apiClient.getArticles(params),
    enabled: isAuthenticated, // Only fetch when authenticated
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
};

// Get single article hook
export const useArticle = (id: string) => {
  return useQuery({
    queryKey: articleKeys.detail(id),
    queryFn: () => apiClient.getArticle(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

// Get article stats hook
export const useArticleStats = () => {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: articleKeys.stats(),
    queryFn: () => apiClient.getArticleStats(),
    enabled: isAuthenticated, // Only fetch when authenticated
    staleTime: 30 * 1000, // 30 seconds
    gcTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Create article mutation
export const useCreateArticle = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (article: ArticleCreate) => apiClient.createArticle(article),
    onSuccess: (newArticle) => {
      // Invalidate and refetch articles
      queryClient.invalidateQueries({ queryKey: articleKeys.lists() });

      // Update stats
      queryClient.invalidateQueries({ queryKey: articleKeys.stats() });

      // Add to cache
      queryClient.setQueryData(articleKeys.detail(newArticle.id), newArticle);
    },
    onError: (error: ApiError) => {
      console.error('Failed to create article:', error);
    },
  });
};

// Update article mutation
export const useUpdateArticle = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, article }: { id: string; article: ArticleUpdate }) =>
      apiClient.updateArticle(id, article),
    onSuccess: (updatedArticle) => {
      // Update the article in cache
      queryClient.setQueryData(articleKeys.detail(updatedArticle.id), updatedArticle);

      // Invalidate lists to refetch
      queryClient.invalidateQueries({ queryKey: articleKeys.lists() });

      // Update stats
      queryClient.invalidateQueries({ queryKey: articleKeys.stats() });
    },
    onError: (error: ApiError) => {
      console.error('Failed to update article:', error);
    },
  });
};

// Delete article mutation
export const useDeleteArticle = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.deleteArticle(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: articleKeys.detail(deletedId) });

      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: articleKeys.lists() });

      // Update stats
      queryClient.invalidateQueries({ queryKey: articleKeys.stats() });
    },
    onError: (error: ApiError) => {
      console.error('Failed to delete article:', error);
    },
  });
};

// Prefetch article for optimistic loading
export const prefetchArticle = (queryClient: ReturnType<typeof useQueryClient>, id: string) => {
  return queryClient.prefetchQuery({
    queryKey: articleKeys.detail(id),
    queryFn: () => apiClient.getArticle(id),
    staleTime: 5 * 60 * 1000,
  });
};

// Optimistic update helper
export const updateArticleOptimistically = (
  queryClient: ReturnType<typeof useQueryClient>,
  id: string,
  updates: Partial<Article>
) => {
  queryClient.setQueryData(articleKeys.detail(id), (old: Article | undefined) => {
    if (!old) return old;
    return { ...old, ...updates };
  });
};