/**
 * Service Worker for offline-first PWA.
 *
 * Strategy:
 * - Static assets: Cache-first (store on install, serve from cache)
 * - API GET requests: Network-first with cache fallback
 * - API mutations: Queue for background sync when offline
 *
 * Note: This file must be compiled to JS before deployment.
 * Service Worker types require: npm install -D @types/serviceworker
 */

/// <reference lib="webworker" />

declare const self: ServiceWorkerGlobalScope;

const CACHE_NAME = 'semilla-v1';
const API_CACHE = 'semilla-api-v1';

const STATIC_ASSETS = [
  '/',
  '/offline',
];

// ── Install ─────────────────────────────────────────────────

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// ── Activate ────────────────────────────────────────────────

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME && key !== API_CACHE)
          .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// ── Fetch ───────────────────────────────────────────────────

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET mutations (handled by background sync)
  if (request.method !== 'GET') return;

  // API requests: network-first with cache fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstWithCache(request));
    return;
  }

  // Static assets: cache-first
  event.respondWith(cacheFirstWithNetwork(request));
});

// ── Strategies ──────────────────────────────────────────────

async function networkFirstWithCache(request: Request): Promise<Response> {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(API_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    return new Response(
      JSON.stringify({ error: 'offline', message: 'You are offline.' }),
      { status: 503, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

async function cacheFirstWithNetwork(request: Request): Promise<Response> {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      const offlinePage = await caches.match('/offline');
      if (offlinePage) return offlinePage;
    }
    return new Response('Offline', { status: 503 });
  }
}

// ── Background Sync (for offline mutations) ─────────────────

self.addEventListener('sync', ((event: any) => {
  if (event.tag === 'offline-mutations') {
    event.waitUntil(replayOfflineMutations());
  }
}) as EventListener);

async function replayOfflineMutations(): Promise<void> {
  // Mutations are stored in IndexedDB by the frontend
  // and replayed here when connectivity is restored.
  const channel = new BroadcastChannel('sw-sync');
  channel.postMessage({ type: 'REPLAY_MUTATIONS' });
  channel.close();
}

export {};
