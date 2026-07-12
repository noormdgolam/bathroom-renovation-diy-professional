
const CACHE_NAME = 'bath-reno-v2';
const urlsToCache = [
  '/',
  '/assets/css/style.css',
  '/assets/js/main.js',
  '/assets/js/search.js',
  '/searchIndex.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) return response;
        return fetch(event.request).then(function(response) {
            if(!response || response.status !== 200 || response.type !== 'basic') return response;
            var responseToCache = response.clone();
            caches.open(CACHE_NAME).then(function(cache) { cache.put(event.request, responseToCache); });
            return response;
          }
        );
      })
  );
});
