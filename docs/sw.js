const CACHE = "holdem-drill-1.0.0";
const CORE = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png", "av/gto-1.webp", "av/gto-2.webp", "av/gto-3.webp", "av/gto-4.webp", "av/gto.webp", "av/lag-1.webp", "av/lag-2.webp", "av/lag-3.webp", "av/lag-4.webp", "av/lag.webp", "av/live-1.webp", "av/live-2.webp", "av/live-3.webp", "av/live-4.webp", "av/live.webp", "av/maniac-1.webp", "av/maniac-2.webp", "av/maniac-3.webp", "av/maniac-4.webp", "av/maniac.webp", "av/nit-1.webp", "av/nit-2.webp", "av/nit-3.webp", "av/nit-4.webp", "av/nit.webp", "av/omc-1.webp", "av/omc-2.webp", "av/omc-3.webp", "av/omc-4.webp", "av/omc.webp", "av/station-1.webp", "av/station-2.webp", "av/station-3.webp", "av/station-4.webp", "av/station.webp", "av/tag-1.webp", "av/tag-2.webp", "av/tag-3.webp", "av/tag-4.webp", "av/tag.webp", "av/weak-1.webp", "av/weak-2.webp", "av/weak-3.webp", "av/weak-4.webp", "av/weak.webp", "av/whale-1.webp", "av/whale-2.webp", "av/whale-3.webp", "av/whale-4.webp", "av/whale.webp"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
// Réseau d'abord (mises à jour immédiates), cache en secours (hors ligne).
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  e.respondWith(fetch(e.request).then(r => {
    const copy = r.clone();
    caches.open(CACHE).then(c => c.put(e.request, copy));
    return r;
  }).catch(() => caches.match(e.request, { ignoreSearch: true })));
});
