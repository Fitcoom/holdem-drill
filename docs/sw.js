const CACHE = "exploit-poker-trainer-ff32b43ec1";
const CORE = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png", "av/fakereg-1.webp", "av/fakereg-2.webp", "av/fakereg-3.webp", "av/fakereg-4.webp", "av/fakereg.webp", "av/fitfold-1.webp", "av/fitfold-2.webp", "av/fitfold-3.webp", "av/fitfold-4.webp", "av/fitfold.webp", "av/gto-1.webp", "av/gto-2.webp", "av/gto-3.webp", "av/gto-4.webp", "av/gto.webp", "av/lag-1.webp", "av/lag-2.webp", "av/lag-3.webp", "av/lag-4.webp", "av/lag.webp", "av/live-1.webp", "av/live-2.webp", "av/live-3.webp", "av/live-4.webp", "av/live.webp", "av/maniac-1.webp", "av/maniac-2.webp", "av/maniac-3.webp", "av/maniac-4.webp", "av/maniac.webp", "av/nit-1.webp", "av/nit-2.webp", "av/nit-3.webp", "av/nit-4.webp", "av/nit.webp", "av/omc-1.webp", "av/omc-2.webp", "av/omc-3.webp", "av/omc-4.webp", "av/omc.webp", "av/seat-1.webp", "av/seat-2.webp", "av/seat-3.webp", "av/seat-4.webp", "av/seat-5.webp", "av/seat-6.webp", "av/seat-7.webp", "av/seat-8.webp", "av/station-1.webp", "av/station-2.webp", "av/station-3.webp", "av/station-4.webp", "av/station.webp", "av/tag-1.webp", "av/tag-2.webp", "av/tag-3.webp", "av/tag-4.webp", "av/tag.webp", "av/weak-1.webp", "av/weak-2.webp", "av/weak-3.webp", "av/weak-4.webp", "av/weak.webp", "av/whale-1.webp", "av/whale-2.webp", "av/whale-3.webp", "av/whale-4.webp", "av/whale.webp", "ui/ic-fast.webp", "ui/ic-gear.webp", "ui/ic-instant.webp", "ui/ic-mixed.webp", "ui/ic-nav-defense.webp", "ui/ic-nav-equity.webp", "ui/ic-nav-more.webp", "ui/ic-nav-play.webp", "ui/ic-nav-potodds.webp", "ui/ic-nav-preflop.webp", "ui/ic-nav-showdown.webp", "ui/ic-nav-stats.webp", "ui/ic-nav-villains.webp", "ui/ic-normal.webp", "ui/ic-read.webp", "ui/ic-slow.webp", "ui/ic-table.webp", "ui/ic-undo.webp", "ui/logo.webp", "ui/rk-chart.webp", "ui/rk-fish.webp", "ui/rk-leak.webp", "ui/rk-legend.webp", "ui/rk-medal.webp", "ui/rk-reg.webp", "ui/rk-shark.webp", "ui/rk-student.webp", "ui/rk-target.webp"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
// Réseau d'abord en contournant le cache HTTP (mises à jour immédiates), cache en secours (hors ligne).
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(fetch(e.request, { cache: "no-cache" }).then(r => {
    const copy = r.clone();
    caches.open(CACHE).then(c => c.put(e.request, copy));
    return r;
  }).catch(() => caches.match(e.request, { ignoreSearch: true })));
});
