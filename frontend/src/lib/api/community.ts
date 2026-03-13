/**
 * Community API hooks using TanStack Query.
 * Covers spaces, topics, posts, reactions, member profiles, leaderboard.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiPost, apiPatch, apiDelete } from '@/lib/api';

// ── Types ──────────────────────────────────────────────────

export interface Space {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon_emoji: string;
  is_active: boolean;
  is_default: boolean;
  is_public: boolean;
  requires_level: number;
  position: number;
  topic_count: number;
  created_at: string;
}

export interface Topic {
  id: number;
  space: number;
  space_name?: string;
  title: string;
  slug: string;
  content_mdx?: string;
  topic_type: 'discussion' | 'question' | 'poll' | 'announcement';
  is_pinned: boolean;
  is_locked: boolean;
  is_answered: boolean;
  reply_count: number;
  like_count: number;
  view_count: number;
  author: number;
  author_name: string;
  created_at: string;
  updated_at?: string;
  last_activity_at: string;
}

export interface Post {
  id: number;
  topic: number;
  author: number;
  author_name: string;
  parent: number | null;
  content: string;
  like_count: number;
  is_answer: boolean;
  reply_count: number;
  created_at: string;
  updated_at: string;
}

export interface Reaction {
  id: number;
  user: number;
  topic: number | null;
  post: number | null;
  reaction_type: 'like' | 'love' | 'insightful' | 'celebrate';
  created_at: string;
}

export interface MemberProfile {
  id: number;
  user: number;
  user_email: string;
  user_name: string;
  bio: string;
  avatar_url: string;
  points: number;
  level: number;
  level_name: string;
  topics_created: number;
  posts_created: number;
  likes_received: number;
  likes_given: number;
  joined_community_at: string;
  last_active_at: string;
}

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ── Query Keys ─────────────────────────────────────────────

export const communityKeys = {
  all: ['community'] as const,
  spaces: () => [...communityKeys.all, 'spaces'] as const,
  topics: (spaceId?: number) => [...communityKeys.all, 'topics', spaceId] as const,
  topic: (id: number) => [...communityKeys.all, 'topic', id] as const,
  posts: (topicId: number) => [...communityKeys.all, 'posts', topicId] as const,
  members: () => [...communityKeys.all, 'members'] as const,
  myProfile: () => [...communityKeys.all, 'me'] as const,
  leaderboard: () => [...communityKeys.all, 'leaderboard'] as const,
};

// ── Spaces ─────────────────────────────────────────────────

export function useSpaces() {
  return useQuery({
    queryKey: communityKeys.spaces(),
    queryFn: () => apiGet<PaginatedResponse<Space>>('/api/v1/community/spaces/'),
  });
}

export function useCreateSpace() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Space>) =>
      apiPost<Space>('/api/v1/community/spaces/', data),
    onSuccess: () => qc.invalidateQueries({ queryKey: communityKeys.spaces() }),
  });
}

// ── Topics ─────────────────────────────────────────────────

export function useTopics(spaceId?: number) {
  const qs = spaceId ? `?space=${spaceId}` : '';
  return useQuery({
    queryKey: communityKeys.topics(spaceId),
    queryFn: () => apiGet<PaginatedResponse<Topic>>(
      `/api/v1/community/topics/${qs}`
    ),
  });
}

export function useTopic(id: number) {
  return useQuery({
    queryKey: communityKeys.topic(id),
    queryFn: () => apiGet<Topic>(`/api/v1/community/topics/${id}/`),
    enabled: !!id,
  });
}

export function useCreateTopic() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { space: number; title: string; content_mdx: string; topic_type?: string }) =>
      apiPost<Topic>('/api/v1/community/topics/', data),
    onSuccess: () => qc.invalidateQueries({ queryKey: communityKeys.all }),
  });
}

// ── Posts ───────────────────────────────────────────────────

export function usePosts(topicId: number) {
  return useQuery({
    queryKey: communityKeys.posts(topicId),
    queryFn: () => apiGet<PaginatedResponse<Post>>(
      `/api/v1/community/posts/?topic=${topicId}`
    ),
    enabled: !!topicId,
  });
}

export function useCreatePost() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { topic: number; content: string; parent?: number }) =>
      apiPost<Post>('/api/v1/community/posts/', data),
    onSuccess: () => qc.invalidateQueries({ queryKey: communityKeys.all }),
  });
}

export function useAcceptAnswer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (postId: number) =>
      apiPost(`/api/v1/community/posts/${postId}/accept-answer/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: communityKeys.all }),
  });
}

// ── Reactions ──────────────────────────────────────────────

export function useAddReaction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { topic?: number; post?: number; reaction_type: string }) =>
      apiPost<Reaction>('/api/v1/community/reactions/', data),
    onSuccess: () => qc.invalidateQueries({ queryKey: communityKeys.all }),
  });
}

export function useRemoveReaction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (reactionId: number) =>
      apiDelete(`/api/v1/community/reactions/${reactionId}/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: communityKeys.all }),
  });
}

// ── Member Profiles ────────────────────────────────────────

export function useMyProfile() {
  return useQuery({
    queryKey: communityKeys.myProfile(),
    queryFn: () => apiGet<MemberProfile>('/api/v1/community/members/me/'),
  });
}

export function useLeaderboard() {
  return useQuery({
    queryKey: communityKeys.leaderboard(),
    queryFn: () => apiGet<MemberProfile[]>('/api/v1/community/members/leaderboard/'),
  });
}
