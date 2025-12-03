// Service Worker for Instagram Automation PWA
const CACHE_NAME = 'instagram-automation-v1';
const STATIC_CACHE = 'instagram-automation-static-v1';

// Files to cache
const urlsToCache = [
  '/',
  '/static/app.js',
  '/static/styles.css',
  '/manifest.json',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
  'https://cdn.jsdelivr.net/npm/chart.js'
];

// Install event - cache static assets
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');

  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('Service Worker: Static assets cached');
        return self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');

  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE && cacheName !== CACHE_NAME) {
              console.log('Service Worker: Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip external API requests
  if (url.origin !== self.location.origin) {
    return;
  }

  // Strategy: Cache first for static assets, network first for API
  if (url.pathname.startsWith('/api/')) {
    // Network first for API calls
    event.respondWith(
      fetch(request)
        .then(response => {
          // Cache successful responses
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(request, responseClone);
              });
          }
          return response;
        })
        .catch(() => {
          // Fallback to cache if network fails
          return caches.match(request);
        })
    );
  } else {
    // Cache first for static assets
    event.respondWith(
      caches.match(request)
        .then(response => {
          if (response) {
            return response;
          }

          // Fetch from network if not in cache
          return fetch(request)
            .then(response => {
              // Cache new responses
              if (response.ok) {
                const responseClone = response.clone();
                caches.open(STATIC_CACHE)
                  .then(cache => {
                    cache.put(request, responseClone);
                  });
              }
              return response;
            });
        })
    );
  }
});

// Background sync for offline job submission
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync-jobs') {
    console.log('Service Worker: Background sync for jobs');

    event.waitUntil(
      // Process any queued jobs from IndexedDB
      processQueuedJobs()
    );
  }
});

// Process queued jobs when back online
async function processQueuedJobs() {
  try {
    // Get queued jobs from IndexedDB
    const queuedJobs = await getQueuedJobs();

    for (const job of queuedJobs) {
      try {
        // Retry the job submission
        const response = await fetch('/api/start-job', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(job.data)
        });

        if (response.ok) {
          // Remove from queue if successful
          await removeJobFromQueue(job.id);
          console.log('Service Worker: Job submitted successfully:', job.id);
        }
      } catch (error) {
        console.error('Service Worker: Failed to submit job:', job.id, error);
      }
    }
  } catch (error) {
    console.error('Service Worker: Error processing queued jobs:', error);
  }
}

// IndexedDB helper functions (simplified)
function getQueuedJobs() {
  return new Promise((resolve) => {
    // In a real implementation, use IndexedDB to store queued jobs
    // For now, return empty array
    resolve([]);
  });
}

function removeJobFromQueue(jobId) {
  return new Promise((resolve) => {
    // Remove job from IndexedDB
    resolve();
  });
}

// Push notifications for job completion
self.addEventListener('push', event => {
  const options = {
    body: 'Your Instagram content is ready!',
    icon: '/static/icon-192.png',
    badge: '/static/badge-72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Results',
        icon: '/static/checkmark.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/static/xmark.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('Instagram Automation', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'explore') {
    // Open the app to the dashboard
    event.waitUntil(
      clients.openWindow('/dashboard')
    );
  }
});

// Message handling for cache updates
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'CACHE_UPDATE') {
    // Update cache with new data
    caches.open(CACHE_NAME).then(cache => {
      cache.put(event.data.url, event.data.response.clone());
    });
  }
});