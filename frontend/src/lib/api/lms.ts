/**
 * LMS API hooks using TanStack Query.
 * Covers courses, sections, lessons, enrollments, progress, certificates, reviews.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiPost, apiPatch, apiDelete } from '@/lib/api';

// ── Types ──────────────────────────────────────────────────

export interface Course {
  id: number;
  title: string;
  slug: string;
  description: string;
  description_mdx?: string;
  thumbnail_url: string;
  preview_video_url: string;
  status: 'draft' | 'published' | 'archived';
  is_featured: boolean;
  is_published: boolean;
  pricing_type: 'free' | 'paid' | 'subscription';
  price: string;
  currency: string;
  stripe_price_id: string;
  stripe_product_id: string;
  level: 'beginner' | 'intermediate' | 'advanced';
  estimated_hours: number;
  tags: string[];
  requirements: string[];
  what_you_learn: string[];
  instructor: number | null;
  instructor_name: string;
  sections?: Section[];
  total_lessons?: number;
  total_enrolled?: number;
  published_at: string | null;
  created_at: string;
  updated_at?: string;
}

export interface Section {
  id: number;
  course: number;
  title: string;
  description: string;
  order: number;
  lesson_count: number;
}

export interface Lesson {
  id: number;
  course: number;
  section: number | null;
  title: string;
  slug: string;
  order: number;
  content_type: 'video' | 'text' | 'quiz' | 'assignment';
  content?: string;
  video_url: string;
  duration_minutes: number;
  is_preview: boolean;
  is_published: boolean;
}

export interface Enrollment {
  id: number;
  user: number;
  course: number;
  course_title: string;
  status: 'active' | 'completed' | 'expired' | 'refunded';
  progress: number;
  amount_paid: string;
  currency: string;
  enrolled_at: string;
  completed_at: string | null;
}

export interface Certificate {
  id: number;
  enrollment: number;
  certificate_number: string;
  issued_at: string;
  pdf_url: string;
  course_title: string;
  user_email: string;
}

export interface Review {
  id: number;
  user: number;
  course: number;
  rating: number;
  comment: string;
  user_name: string;
  created_at: string;
}

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ── Query Keys ─────────────────────────────────────────────

export const lmsKeys = {
  all: ['lms'] as const,
  courses: () => [...lmsKeys.all, 'courses'] as const,
  course: (id: number) => [...lmsKeys.courses(), id] as const,
  sections: (courseId: number) => [...lmsKeys.all, 'sections', courseId] as const,
  lessons: (courseId?: number) => [...lmsKeys.all, 'lessons', courseId] as const,
  enrollments: () => [...lmsKeys.all, 'enrollments'] as const,
  certificates: () => [...lmsKeys.all, 'certificates'] as const,
  reviews: (courseId: number) => [...lmsKeys.all, 'reviews', courseId] as const,
};

// ── Courses ────────────────────────────────────────────────

export function useCourses(params?: { status?: string; level?: string }) {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set('status', params.status);
  if (params?.level) searchParams.set('level', params.level);
  const qs = searchParams.toString();

  return useQuery({
    queryKey: [...lmsKeys.courses(), params],
    queryFn: () => apiGet<PaginatedResponse<Course>>(
      `/api/v1/lms/courses/${qs ? `?${qs}` : ''}`
    ),
  });
}

export function useCourse(id: number) {
  return useQuery({
    queryKey: lmsKeys.course(id),
    queryFn: () => apiGet<Course>(`/api/v1/lms/courses/${id}/`),
    enabled: !!id,
  });
}

export function useCreateCourse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Course>) =>
      apiPost<Course>('/api/v1/lms/courses/', data),
    onSuccess: () => qc.invalidateQueries({ queryKey: lmsKeys.courses() }),
  });
}

export function useUpdateCourse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }: Partial<Course> & { id: number }) =>
      apiPatch<Course>(`/api/v1/lms/courses/${id}/`, data),
    onSuccess: (_, v) => {
      qc.invalidateQueries({ queryKey: lmsKeys.course(v.id) });
      qc.invalidateQueries({ queryKey: lmsKeys.courses() });
    },
  });
}

// ── Lessons ────────────────────────────────────────────────

export function useLessons(courseId?: number) {
  const qs = courseId ? `?course=${courseId}` : '';
  return useQuery({
    queryKey: lmsKeys.lessons(courseId),
    queryFn: () => apiGet<PaginatedResponse<Lesson>>(`/api/v1/lms/lessons/${qs}`),
  });
}

export function useCreateLesson() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Lesson>) =>
      apiPost<Lesson>('/api/v1/lms/lessons/', data),
    onSuccess: () => qc.invalidateQueries({ queryKey: lmsKeys.all }),
  });
}

// ── Enrollments ────────────────────────────────────────────

export function useMyEnrollments() {
  return useQuery({
    queryKey: lmsKeys.enrollments(),
    queryFn: () => apiGet<PaginatedResponse<Enrollment>>('/api/v1/lms/enrollments/'),
  });
}

export function useEnroll() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { course: number }) =>
      apiPost<Enrollment>('/api/v1/lms/enrollments/', data),
    onSuccess: () => qc.invalidateQueries({ queryKey: lmsKeys.enrollments() }),
  });
}

export function useCompleteEnrollment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (enrollmentId: number) =>
      apiPost(`/api/v1/lms/enrollments/${enrollmentId}/complete/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: lmsKeys.enrollments() });
      qc.invalidateQueries({ queryKey: lmsKeys.certificates() });
    },
  });
}

// ── Reviews ────────────────────────────────────────────────

export function useReviews(courseId: number) {
  return useQuery({
    queryKey: lmsKeys.reviews(courseId),
    queryFn: () => apiGet<PaginatedResponse<Review>>(
      `/api/v1/lms/reviews/?course=${courseId}`
    ),
    enabled: !!courseId,
  });
}

export function useCreateReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { course: number; rating: number; comment: string }) =>
      apiPost<Review>('/api/v1/lms/reviews/', data),
    onSuccess: () => qc.invalidateQueries({ queryKey: lmsKeys.all }),
  });
}

// ── Certificates ───────────────────────────────────────────

export function useMyCertificates() {
  return useQuery({
    queryKey: lmsKeys.certificates(),
    queryFn: () => apiGet<PaginatedResponse<Certificate>>('/api/v1/lms/certificates/'),
  });
}
