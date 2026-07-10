const CACHE_NAME = 'articlio-cache-v5';
const urlsToCache = [
  '/',
  '/manifest.json',
];

// Install event: cache essential resources and skip waiting
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event: Network-First for HTML navigation and root requests, Cache-First for static assets
self.addEventListener('fetch', event => {
  // Only handle GET requests. POST/PUT etc. should go straight to the network.
  if (event.request.method !== 'GET') {
    return;
  }

  const url = new URL(event.request.url);

  // Bypass service worker for Google Analytics, Tag Manager, and Ads to prevent tracking/CSP fetch errors
  if (
    url.hostname.includes('google-analytics.com') || 
    url.hostname.includes('googletagmanager.com') ||
    url.hostname.includes('googleads') ||
    url.hostname.includes('doubleclick')
  ) {
    return;
  }

  // Use a Network-First strategy for the root path and page navigations
  if (event.request.mode === 'navigate' || url.pathname === '/') {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // If response is valid, update the cache
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Offline fallback: try to serve from cache
          return caches.match(event.request);
        })
    );
  } else {
    // Cache-First, falling back to Network for assets
    event.respondWith(
      caches.match(event.request)
        .then(response => {
          if (response) {
            return response;
          }
          return fetch(event.request);
        })
    );
  }
});

// Activate event: clean up old caches and claim clients immediately
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    Promise.all([
      self.clients.claim(),
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheWhitelist.indexOf(cacheName) === -1) {
              return caches.delete(cacheName);
            }
          })
        );
      })
    ])
  );
});
