/**
 * Offline store using Dexie.js (IndexedDB wrapper).
 *
 * Provides:
 * - Local cache for API data (courses, community, CMS content)
 * - Offline mutation queue for background sync
 * - Conflict resolution timestamp tracking
 */

import Dexie, { type EntityTable } from 'dexie';

// ── Offline Mutation Queue ──────────────────────────────────

export interface OfflineMutation {
  id?: number;
  url: string;
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body: string;
  headers: Record<string, string>;
  createdAt: number;
  retryCount: number;
  status: 'pending' | 'syncing' | 'failed';
}

// ── Cached API Data ─────────────────────────────────────────

export interface CachedItem {
  id?: number;
  key: string; // e.g. "courses:list" or "course:42"
  data: string; // JSON-serialized API response
  cachedAt: number;
  expiresAt: number;
}

// ── Database Schema ─────────────────────────────────────────

class OfflineDatabase extends Dexie {
  mutations!: EntityTable<OfflineMutation, 'id'>;
  cache!: EntityTable<CachedItem, 'id'>;

  constructor() {
    super('semilla-offline');
    this.version(1).stores({
      mutations: '++id, status, createdAt',
      cache: '++id, &key, expiresAt',
    });
  }
}

export const db = new OfflineDatabase();

// ── Mutation Queue API ──────────────────────────────────────

export async function queueMutation(mutation: Omit<OfflineMutation, 'id' | 'retryCount' | 'status'>): Promise<void> {
  await db.mutations.add({
    ...mutation,
    retryCount: 0,
    status: 'pending',
  });

  // Request background sync if available
  if ('serviceWorker' in navigator && 'SyncManager' in window) {
    const reg = await navigator.serviceWorker.ready;
    await (reg as any).sync.register('offline-mutations');
  }
}

export async function getPendingMutations(): Promise<OfflineMutation[]> {
  return db.mutations.where('status').equals('pending').sortBy('createdAt');
}

export async function markMutationSynced(id: number): Promise<void> {
  await db.mutations.delete(id);
}

export async function markMutationFailed(id: number): Promise<void> {
  await db.mutations.update(id, {
    status: 'failed',
    retryCount: (await db.mutations.get(id))?.retryCount ?? 0 + 1,
  });
}

// ── Cache API ───────────────────────────────────────────────

const DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes

export async function getCached<T>(key: string): Promise<T | null> {
  const item = await db.cache.where('key').equals(key).first();
  if (!item) return null;
  if (Date.now() > item.expiresAt) {
    await db.cache.delete(item.id!);
    return null;
  }
  return JSON.parse(item.data) as T;
}

export async function setCache(key: string, data: unknown, ttlMs = DEFAULT_TTL): Promise<void> {
  const existing = await db.cache.where('key').equals(key).first();
  const record: Omit<CachedItem, 'id'> = {
    key,
    data: JSON.stringify(data),
    cachedAt: Date.now(),
    expiresAt: Date.now() + ttlMs,
  };

  if (existing) {
    await db.cache.update(existing.id!, record);
  } else {
    await db.cache.add(record as CachedItem);
  }
}

export async function clearCache(): Promise<void> {
  await db.cache.clear();
}

// ── Sync Listener ───────────────────────────────────────────

if (typeof window !== 'undefined') {
  const channel = new BroadcastChannel('sw-sync');
  channel.addEventListener('message', async (event: MessageEvent) => {
    if (event.data?.type === 'REPLAY_MUTATIONS') {
      const mutations = await getPendingMutations();
      for (const mutation of mutations) {
        try {
          const res = await fetch(mutation.url, {
            method: mutation.method,
            headers: mutation.headers,
            body: mutation.body,
          });
          if (res.ok) {
            await markMutationSynced(mutation.id!);
          } else {
            await markMutationFailed(mutation.id!);
          }
        } catch {
          await markMutationFailed(mutation.id!);
        }
      }
    }
  });
}
