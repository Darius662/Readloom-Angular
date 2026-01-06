/**
 * Service Worker for Readloom PWA
 * Handles caching, offline functionality, and background sync
 */

const CACHE_NAME = 'readloom-v1';
const STATIC_CACHE = 'readloom-static-v1';
const DYNAMIC_CACHE = 'readloom-dynamic-v1';
const API_CACHE = 'readloom-api-v1';

// Static assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/js/persistent-preferences.js',
  '/offline'
];

// Install event - cache static assets
self.addEventListener('install', event => {
  console.log('Service Worker installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('Caching static assets');
        // Cache assets, but don't fail if some are missing
        return Promise.all(
          STATIC_ASSETS.map(url => {
            return cache.add(url).catch(err => {
              console.warn(`Failed to cache ${url}:`, err);
            });
          })
        );
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== STATIC_CACHE && 
              cacheName !== DYNAMIC_CACHE && 
              cacheName !== API_CACHE) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip chrome extensions and other non-http requests
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // API requests - Network first, fall back to cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstStrategy(request, API_CACHE));
    return;
  }

  // Static assets - Cache first, fall back to network
  if (isStaticAsset(url.pathname)) {
    event.respondWith(cacheFirstStrategy(request, STATIC_CACHE));
    return;
  }

  // HTML pages - Network first, fall back to cache
  if (request.headers.get('accept').includes('text/html')) {
    event.respondWith(networkFirstStrategy(request, DYNAMIC_CACHE));
    return;
  }

  // Default - Network first
  event.respondWith(networkFirstStrategy(request, DYNAMIC_CACHE));
});

/**
 * Cache first strategy - try cache first, fall back to network
 */
function cacheFirstStrategy(request, cacheName) {
  return caches.match(request)
    .then(response => {
      if (response) {
        return response;
      }
      return fetch(request)
        .then(response => {
          // Don't cache non-successful responses
          if (!response || response.status !== 200 || response.type === 'error') {
            return response;
          }
          // Clone and cache the response
          const responseClone = response.clone();
          caches.open(cacheName)
            .then(cache => cache.put(request, responseClone));
          return response;
        });
    })
    .catch(() => {
      // Return offline page if available
      return caches.match('/offline');
    });
}

/**
 * Network first strategy - try network first, fall back to cache
 */
function networkFirstStrategy(request, cacheName) {
  return fetch(request)
    .then(response => {
      // Don't cache non-successful responses
      if (!response || response.status !== 200 || response.type === 'error') {
        return response;
      }
      // Clone and cache the response
      const responseClone = response.clone();
      caches.open(cacheName)
        .then(cache => cache.put(request, responseClone));
      return response;
    })
    .catch(() => {
      // Try to return cached version
      return caches.match(request)
        .then(response => {
          if (response) {
            return response;
          }
          // Return offline page if available
          return caches.match('/offline');
        });
    });
}

/**
 * Check if URL is a static asset
 */
function isStaticAsset(pathname) {
  const staticExtensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.eot'];
  return staticExtensions.some(ext => pathname.endsWith(ext));
}

/**
 * Background sync for queued actions
 */
self.addEventListener('sync', event => {
  if (event.tag === 'sync-queue') {
    event.waitUntil(syncQueuedActions());
  }
});

/**
 * Sync queued actions when connection is restored
 */
function syncQueuedActions() {
  return new Promise((resolve, reject) => {
    // Get queued actions from IndexedDB or localStorage
    const queue = JSON.parse(localStorage.getItem('readloom_sync_queue') || '[]');
    
    if (queue.length === 0) {
      resolve();
      return;
    }

    // Process each queued action
    Promise.all(queue.map(action => {
      return fetch(action.url, {
        method: action.method,
        headers: action.headers,
        body: action.body ? JSON.stringify(action.body) : undefined
      });
    }))
    .then(() => {
      // Clear queue on success
      localStorage.removeItem('readloom_sync_queue');
      resolve();
    })
    .catch(reject);
  });
}

/**
 * Handle push notifications
 */
self.addEventListener('push', event => {
  if (!event.data) {
    return;
  }

  const data = event.data.json();
  const options = {
    body: data.body || 'New notification from Readloom',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-192x192.png',
    tag: data.tag || 'readloom-notification',
    requireInteraction: data.requireInteraction || false,
    actions: data.actions || [],
    data: data.data || {}
  };

  event.waitUntil(
    self.registration.showNotification(data.title || 'Readloom', options)
  );
});

/**
 * Handle notification clicks
 */
self.addEventListener('notificationclick', event => {
  event.notification.close();

  const urlToOpen = event.notification.data.url || '/';

  event.waitUntil(
    clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    })
    .then(clientList => {
      // Check if app is already open
      for (let i = 0; i < clientList.length; i++) {
        const client = clientList[i];
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus();
        }
      }
      // Open new window if not already open
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});

/**
 * Handle notification close
 */
self.addEventListener('notificationclose', event => {
  console.log('Notification closed:', event.notification.tag);
});
