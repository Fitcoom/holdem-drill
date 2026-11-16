"""Construit la version installable (PWA) de Hold'em Drill dans docs/ (servi par GitHub Pages).

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
<meta name="theme-color" content="#1e5a44">
<meta name="description" content="Texas Hold'em poker trainer: preflop ranges, equity, pot odds, showdown.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Hold'em Drill">
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
  "name": "Hold'em Drill",
  "short_name": "Hold'em Drill",
  "description": "Texas Hold'em 6-max poker trainer: preflop ranges, equity, pot odds, showdown.",
  "lang": "en",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#0e1512",
  "theme_color": "#1e5a44",
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
(APP / "sw.js").write_text(f"""const CACHE = "holdem-drill-{VERSION}";
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

def icon(size, maskable=False):
    s = 4  # suréchantillonnage pour l'anticrénelage
    W = size * s
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if maskable:
        d.rectangle([0, 0, W, W], fill=FELT)
    else:
        d.rounded_rectangle([0, 0, W - 1, W - 1], radius=int(W * 0.22), fill=FELT)
    d.ellipse([W * .08, W * .08, W * .92, W * .92], outline=FELT2, width=int(W * .03))
    k = 0.72 if maskable else 1.0  # zone sûre maskable
    cw, ch = W * .46 * k, W * .62 * k
    x0, y0 = (W - cw) / 2 + W * .02, (W - ch) / 2
    # carte de fond inclinée (as de cœur suggéré par une couleur laiton)
    back = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    bd = ImageDraw.Draw(back)
    bd.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], radius=int(cw * .12), fill=BRASS)
    back = back.rotate(14, center=(W / 2, W / 2), resample=Image.BICUBIC)
    im.alpha_composite(back)
    front = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    fd = ImageDraw.Draw(front)
    fx = x0 - W * .05
    fd.rounded_rectangle([fx, y0, fx + cw, y0 + ch], radius=int(cw * .12), fill=CARD, outline=(200, 205, 200), width=int(W * .006))
    f_sym = ImageFont.truetype(SYM, int(ch * .55))
    fd.text((fx + cw / 2, y0 + ch * .56), "♠", font=f_sym, fill=(22, 24, 26), anchor="mm")
    f_a = ImageFont.truetype(DISP, int(ch * .2))
    fd.text((fx + cw * .1, y0 + ch * .05), "A", font=f_a, fill=(22, 24, 26), anchor="la")
    front = front.rotate(-6, center=(W / 2, W / 2), resample=Image.BICUBIC)
    im.alpha_composite(front)
    return im.resize((size, size), Image.LANCZOS)

icon(192).save(APP / "icon-192.png")
icon(512).save(APP / "icon-512.png")
icon(512, maskable=True).save(APP / "icon-maskable-512.png")
ic = icon(180, maskable=True).convert("RGB")  # iOS : pas de transparence
ic.save(APP / "apple-touch-icon.png")
print("OK ->", APP)
