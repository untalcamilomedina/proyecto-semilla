/**
 * Service Worker para Proyecto Semilla PWA
 * Maneja caching, offline-first, push notifications y background sync
 */

const CACHE_NAME = 'proyecto-semilla-v1.0.0';
const STATIC_CACHE = 'proyecto-semilla-static-v1.0.0';
const DYNAMIC_CACHE = 'proyecto-semilla-dynamic-v1.0.0';
const API_CACHE = 'proyecto-semilla-api-v1.0.0';

// Recursos críticos que deben cachearse inmediatamente
const CRITICAL_RESOURCES = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/js/vendor.js',
  '/manifest.json',
  '/offline.html',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'
];

// Recursos estáticos que cambian con menos frecuencia
const STATIC_RESOURCES = [
  '/static/css/',
  '/static/js/',
  '/static/fonts/',
  '/static/images/',
  '/icons/',
  '/manifest.json'
];

// APIs que deben cachearse para offline
const API_ENDPOINTS = [
  '/api/v1/health',
  '/api/v1/user/profile',
  '/api/v1/dashboard',
  '/api/v1/tenants'
];

// Configuración de cache
const CACHE_CONFIG = {
  maxAge: 24 * 60 * 60 * 1000, // 24 horas
  maxEntries: 100,
  strategy: 'network-first' // network-first para APIs, cache-first para estáticos
};

// Install event - cache recursos críticos
self.addEventListener('install', event => {
  console.log('🔧 Service Worker installing...');

  event.waitUntil(
    Promise.all([
      // Cache recursos críticos
      caches.open(STATIC_CACHE).then(cache => {
        console.log('📦 Caching critical resources...');
        return cache.addAll(CRITICAL_RESOURCES);
      }),

      // Skip waiting para activar inmediatamente
      self.skipWaiting()
    ])
  );

  console.log('✅ Service Worker installed');
});

// Activate event - cleanup old caches
self.addEventListener('activate', event => {
  console.log('🚀 Service Worker activating...');

  event.waitUntil(
    Promise.all([
      // Cleanup old caches
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE &&
                cacheName !== DYNAMIC_CACHE &&
                cacheName !== API_CACHE) {
              console.log('🗑️ Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),

      // Take control of all clients
      self.clients.claim()
    ])
  );

  console.log('✅ Service Worker activated');
});

// Fetch event - estrategia de cache inteligente
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') return;

  // Skip external requests
  if (!url.origin.includes(self.location.origin) &&
      !url.origin.includes('api.proyecto-semilla.com')) return;

  // Handle different resource types
  if (isApiRequest(url)) {
    event.respondWith(handleApiRequest(request));
  } else if (isStaticResource(url)) {
    event.respondWith(handleStaticRequest(request));
  } else {
    event.respondWith(handleDynamicRequest(request));
  }
});

// Push notifications
self.addEventListener('push', event => {
  console.log('📱 Push notification received:', event);

  if (!event.data) return;

  const data = event.data.json();

  const options = {
    body: data.body,
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: data.data,
    actions: [
      {
        action: 'view',
        title: 'Ver',
        icon: '/icons/action-view.png'
      },
      {
        action: 'dismiss',
        title: 'Descartar'
      }
    ],
    requireInteraction: true,
    silent: false,
    tag: data.tag || 'general'
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Background sync
self.addEventListener('sync', event => {
  console.log('🔄 Background sync triggered:', event.tag);

  if (event.tag === 'background-sync') {
    event.waitUntil(syncPendingRequests());
  }
});

// Notification click
self.addEventListener('notificationclick', event => {
  console.log('🔔 Notification clicked:', event);

  event.notification.close();

  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow(event.notification.data?.url || '/')
    );
  }
});

// Helper functions
function isApiRequest(url) {
  return API_ENDPOINTS.some(endpoint => url.pathname.startsWith(endpoint)) ||
         url.pathname.includes('/api/');
}

function isStaticResource(url) {
  return STATIC_RESOURCES.some(resource => url.pathname.includes(resource)) ||
         /\.(css|js|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot)$/.test(url.pathname);
}

async function handleApiRequest(request) {
  const cache = await caches.open(API_CACHE);

  try {
    // Network-first strategy for APIs
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
  } catch (error) {
    console.log('🌐 Network failed, trying cache for API:', request.url);
  }

  // Fallback to cache
  const cachedResponse = await cache.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  // Return offline response
  return new Response(JSON.stringify({
    error: 'Offline',
    message: 'No hay conexión a internet'
  }), {
    status: 503,
    headers: { 'Content-Type': 'application/json' }
  });
}

async function handleStaticRequest(request) {
  const cache = await caches.open(STATIC_CACHE);

  // Cache-first strategy for static resources
  const cachedResponse = await cache.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('❌ Static resource failed to load:', request.url);
    return new Response('Resource not available offline', { status: 404 });
  }
}

async function handleDynamicRequest(request) {
  const cache = await caches.open(DYNAMIC_CACHE);

  try {
    // Try network first
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      // Cache successful responses
      if (shouldCacheResponse(networkResponse)) {
        cache.put(request, networkResponse.clone());
      }
      return networkResponse;
    }
  } catch (error) {
    console.log('🌐 Network failed, trying cache for dynamic content');
  }

  // Fallback to cache
  const cachedResponse = await cache.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  // Return offline page for navigation requests
  if (request.mode === 'navigate') {
    const offlineResponse = await caches.match('/offline.html');
    return offlineResponse || new Response('Offline', { status: 503 });
  }

  return new Response('Offline', { status: 503 });
}

function shouldCacheResponse(response) {
  return response.status === 200 &&
         response.type === 'basic' &&
         !response.headers.get('Cache-Control')?.includes('no-cache');
}

async function syncPendingRequests() {
  console.log('🔄 Syncing pending requests...');

  try {
    const cache = await caches.open(API_CACHE);
    const keys = await cache.keys();

    const syncPromises = keys.map(async request => {
      try {
        const response = await fetch(request);
        if (response.ok) {
          await cache.put(request, response);
          console.log('✅ Synced:', request.url);
        }
      } catch (error) {
        console.log('❌ Failed to sync:', request.url, error);
      }
    });

    await Promise.all(syncPromises);
    console.log('✅ Background sync completed');
  } catch (error) {
    console.error('❌ Background sync failed:', error);
  }
}

// Periodic cleanup
setInterval(async () => {
  try {
    const cache = await caches.open(DYNAMIC_CACHE);
    const keys = await cache.keys();

    // Remove old entries
    const deletePromises = keys
      .filter(request => {
        const response = cache.match(request);
        if (response) {
          const date = response.headers.get('date');
          if (date) {
            const age = Date.now() - new Date(date).getTime();
            return age > CACHE_CONFIG.maxAge;
          }
        }
        return false;
      })
      .map(request => cache.delete(request));

    await Promise.all(deletePromises);

    // Limit cache size
    if (keys.length > CACHE_CONFIG.maxEntries) {
      const excessKeys = keys.slice(0, keys.length - CACHE_CONFIG.maxEntries);
      await Promise.all(excessKeys.map(key => cache.delete(key)));
    }

    console.log('🧹 Cache cleanup completed');
  } catch (error) {
    console.error('❌ Cache cleanup failed:', error);
  }
}, 30 * 60 * 1000); // Every 30 minutes

console.log('🎉 Service Worker loaded successfully');