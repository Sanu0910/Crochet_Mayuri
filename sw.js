// Mayuri'z app: lets the site install to a phone's home screen and open
// when offline. Always tries the live site first, so new products (pushed by
// the Telegram bot) show up straight away; saved copies are only a fallback.
// Bump VERSION to drop old saved copies.
const VERSION = 'mz-v2';
const START = ['/', '/media/icon.svg', '/media/icon-192.png', '/manifest.webmanifest'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(START)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  const url = new URL(req.url);
  // Only this site's own GET requests; order form, fonts and EmailJS go straight out.
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;

  e.respondWith(
    fetch(req)
      .then(res => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(VERSION).then(c => c.put(req, copy));
        }
        return res;
      })
      .catch(() =>
        caches.match(req, { ignoreSearch: req.mode === 'navigate' })
          .then(hit => hit || (req.mode === 'navigate' ? caches.match('/') : undefined))
          .then(hit => hit || Response.error())
      )
  );
});
