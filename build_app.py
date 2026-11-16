"""Construit la version installable (PWA) d'Exploit Poker Trainer dans docs/ (servi par GitHub Pages).

Source unique : index.html (aussi publié comme artifact claude.ai).
Usage : python build_app.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
APP = ROOT / "docs"
APP.mkdir(exist_ok=True)
import hashlib
# Version = empreinte du contenu : chaque build modifié change sw.js, donc le navigateur voit la mise à jour.
VERSION = hashlib.sha1((ROOT / "index.html").read_bytes() + b"".join(f.read_bytes() for f in sorted((ROOT / "av").glob("*.webp")) + sorted((ROOT / "ui").glob("*.webp")))).hexdigest()[:10]

FELT, FELT2, CARD, BRASS = (30, 90, 68), (20, 66, 50), (251, 251, 248), (216, 167, 72)

# ---------- index.html ----------
body = (ROOT / "index.html").read_text(encoding="utf-8")
head = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0e1512">
<meta name="description" content="Exploit Poker Trainer: learn to read and exploit poker players. Play the player, not the chart.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Exploit">
<style>
:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;-webkit-tap-highlight-color:transparent}
img{max-width:100%}
[hidden]{display:none!important}
</style>
"""
sw_reg = """
<script>
if ("serviceWorker" in navigator) {
  // Vérifie les mises à jour à chaque visite (et toutes les 30 min), sans passer par le cache HTTP,
  // puis recharge une fois quand la nouvelle version prend le relais.
  const hadController = !!navigator.serviceWorker.controller;
  let reloaded = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => { if (hadController && !reloaded) { reloaded = true; location.reload(); } });
  window.addEventListener("load", () => navigator.serviceWorker.register("sw.js", { updateViaCache: "none" })
    .then(r => { r.update(); setInterval(() => r.update(), 30 * 60 * 1000); }).catch(() => {}));
}
</script>
</body>
</html>
"""
# Le <title>, les <link> de polices et le <style> de la source restent dans <body> :
# on les remonte dans <head> en coupant au premier <div class="wrap">.
cut = body.index('<div class="wrap">')
html = head + body[:cut] + "</head>\n<body>\n" + body[cut:] + sw_reg
(APP / "index.html").write_text(html, encoding="utf-8")

# ---------- manifest ----------
(APP / "manifest.webmanifest").write_text("""{
  "name": "Exploit Poker Trainer",
  "short_name": "Exploit",
  "description": "Exploit Poker Trainer: learn to read and exploit poker players. Play the player, not the chart.",
  "lang": "en",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#0e1512",
  "theme_color": "#0e1512",
  "categories": ["games", "education"],
  "icons": [
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]
}
""", encoding="utf-8")

# ---------- portraits (av/*.webp) ----------
import shutil
(APP / "av").mkdir(exist_ok=True)
AV = sorted((ROOT / "av").glob("*.webp"))
for f in AV:
    shutil.copy2(f, APP / "av" / f.name)
UI = sorted((ROOT / "ui").glob("*.webp"))
(APP / "ui").mkdir(exist_ok=True)
for f in UI:
    shutil.copy2(f, APP / "ui" / f.name)
AVS = ", ".join([f'"av/{f.name}"' for f in AV] + [f'"ui/{f.name}"' for f in UI])

# ---------- service worker (hors ligne) ----------
(APP / "sw.js").write_text(f"""const CACHE = "exploit-poker-trainer-{VERSION}";
const CORE = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png", {AVS}];
self.addEventListener("install", e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
}});
self.addEventListener("activate", e => {{
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
}});
// Réseau d'abord en contournant le cache HTTP (mises à jour immédiates), cache en secours (hors ligne).
self.addEventListener("fetch", e => {{
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(fetch(e.request, {{ cache: "no-cache" }}).then(r => {{
    const copy = r.clone();
    caches.open(CACHE).then(c => c.put(e.request, copy));
    return r;
  }}).catch(() => caches.match(e.request, {{ ignoreSearch: true }})));
}});
""", encoding="utf-8")

# ---------- icônes ----------
SYM = "C:/Windows/Fonts/seguisym.ttf"
DISP = "C:/Windows/Fonts/impact.ttf"

LOGO = Image.open(ROOT / "brand" / "logo-1024.png").convert("RGB")
BG = (14, 21, 18)

def icon(size, maskable=False):
    """App icons from the illustrated logo; maskable versions keep it inside the safe zone."""
    if not maskable:
        return LOGO.resize((size, size), Image.LANCZOS)
    im = Image.new("RGB", (size, size), BG)
    k = int(size * .8)
    im.paste(LOGO.resize((k, k), Image.LANCZOS), ((size - k) // 2, (size - k) // 2))
    return im

icon(192).save(APP / "icon-192.png")
icon(512).save(APP / "icon-512.png")
icon(512, maskable=True).save(APP / "icon-maskable-512.png")
ic = icon(180, maskable=True).convert("RGB")  # iOS : pas de transparence
ic.save(APP / "apple-touch-icon.png")
print("OK ->", APP)
