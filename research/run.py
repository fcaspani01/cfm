"""Ricerca di design eseguita su GitHub Actions: scoperta siti, screenshot, candidati immagini."""
import json, re, sys, time, urllib.parse
from pathlib import Path
import requests
from PIL import Image, ImageDraw

OUT = Path("research/out"); OUT.mkdir(parents=True, exist_ok=True)
cfg = json.loads(Path("research/config.json").read_text())
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36 CFM-design-research"}
log = []

# 1. Scoperta: link esterni nelle pagine elenco
found = {}
for url in cfg.get("discover", []):
    try:
        html = requests.get(url, headers=UA, timeout=30).text
        host = urllib.parse.urlparse(url).netloc
        links = set()
        for h in re.findall(r'href="(https?://[^"#]+)"', html):
            d = urllib.parse.urlparse(h).netloc.lower()
            if d and host.split(".")[-2] not in d and not re.search(
                r"facebook|twitter|instagram|linkedin|youtube|google|apple|wordpress|gravatar|pinterest|x\.com|tiktok|cookie|iubenda|w3\.org|schema\.org|cloudflare|jquery|bootstrap|fonts|amazon|microsoft|whatsapp|virgilio|italiaonline|paginegialle|freshysites|simpro|colorlib|isotropic", d):
                links.add(f"{urllib.parse.urlparse(h).scheme}://{d}/")
        found[url] = sorted(links)
    except Exception as e:
        found[url] = [f"ERRORE {e}"]
(OUT / "discovered.json").write_text(json.dumps(found, indent=1))

# 2. Screenshot dei siti
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    for i, url in enumerate(cfg.get("screens", [])):
        slug = re.sub(r"[^a-z0-9]+", "-", url.lower().split("//")[1]).strip("-")[:50]
        for name, vp in (("desk", {"width": 1366, "height": 860}), ("mob", {"width": 390, "height": 844})):
            try:
                ctx = b.new_context(viewport=vp, locale="it-IT", user_agent=UA["User-Agent"] if name == "desk" else None,
                                    is_mobile=name == "mob", device_scale_factor=1)
                pg = ctx.new_page()
                pg.goto(url, wait_until="domcontentloaded", timeout=45000)
                pg.wait_for_timeout(3500)
                for sel in ["text=/accett/i", "text=/accept/i", "text=/consent/i", "#onetrust-accept-btn-handler"]:
                    try: pg.locator(sel).first.click(timeout=1200); break
                    except Exception: pass
                pg.wait_for_timeout(800)
                h = min(pg.evaluate("document.documentElement.scrollHeight"), 5200 if name == "desk" else 3600)
                pg.set_viewport_size({"width": vp["width"], "height": h})
                pg.wait_for_timeout(1200)
                pg.screenshot(path=str(OUT / f"s{i:02d}-{slug}-{name}.jpg"), type="jpeg", quality=60, full_page=False)
                ctx.close()
            except Exception as e:
                log.append(f"screen {url} {name}: {e}")
    b.close()

# 3. Candidati immagini (Wikimedia Commons + Openverse), con licenze
def commons(q):
    r = requests.get("https://commons.wikimedia.org/w/api.php", headers=UA, timeout=30, params={
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrlimit": 12,
        "gsrsearch": f"{q} filetype:bitmap", "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 480})
    res = []
    for pg in (r.json().get("query", {}).get("pages", {}) or {}).values():
        ii = pg["imageinfo"][0]; md = ii.get("extmetadata", {})
        res.append({"src": "commons", "title": pg["title"], "thumb": ii.get("thumburl"), "url": ii["url"],
                    "page": ii.get("descriptionurl"), "w": ii.get("width"), "h": ii.get("height"),
                    "license": md.get("LicenseShortName", {}).get("value"),
                    "artist": re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", ""))[:80]})
    return res

def openverse(q):
    r = requests.get("https://api.openverse.org/v1/images/", headers=UA, timeout=30, params={
        "q": q, "license_type": "commercial,modification", "page_size": 12})
    return [{"src": "openverse", "title": i.get("title"), "thumb": i.get("thumbnail"), "url": i.get("url"),
             "page": i.get("foreign_landing_url"), "w": i.get("width"), "h": i.get("height"),
             "license": f"{i.get('license')} {i.get('license_version')}", "artist": (i.get("creator") or "")[:80]}
            for i in r.json().get("results", [])]

allimgs = {}
for q in cfg.get("images", []):
    items = []
    for fn in (commons, openverse):
        try: items += fn(q)
        except Exception as e: log.append(f"img {q} {fn.__name__}: {e}")
        time.sleep(1)
    items = [x for x in items if x.get("thumb")][:20]
    allimgs[q] = items
    # foglio provini
    cell, cols = 240, 5
    rows = (len(items) + cols - 1) // cols or 1
    sheet = Image.new("RGB", (cols * cell, rows * (cell + 18)), "white")
    d = ImageDraw.Draw(sheet)
    for k, it in enumerate(items):
        try:
            im = Image.open(requests.get(it["thumb"], headers=UA, timeout=30, stream=True).raw).convert("RGB")
            im.thumbnail((cell - 6, cell - 6))
            x, y = (k % cols) * cell, (k // cols) * (cell + 18)
            sheet.paste(im, (x + 3, y + 3))
            d.rectangle([x, y + cell, x + cell, y + cell + 18], fill="black")
            d.text((x + 4, y + cell + 3), f"{k} {it['src'][:3]} {(it['license'] or '')[:14]} {it['w']}x{it['h']}", fill="white")
        except Exception as e:
            log.append(f"thumb {it['thumb']}: {e}")
    sheet.save(OUT / f"img-{re.sub('[^a-z0-9]+', '-', q.lower())}.jpg", quality=70)
(OUT / "images.json").write_text(json.dumps(allimgs, indent=1, ensure_ascii=False))

# 4. Download delle immagini scelte (opzionale)
sel = cfg.get("download", [])
if sel:
    dl = OUT / "selected"; dl.mkdir(exist_ok=True)
    for s in sel:
        it = allimgs[s["query"]][s["index"]]
        try:
            data = requests.get(it["url"], headers=UA, timeout=60).content
            im = Image.open(__import__("io").BytesIO(data)).convert("RGB")
            im.thumbnail((2000, 2000))
            im.save(dl / f"{s['name']}.jpg", quality=82)
            (dl / f"{s['name']}.json").write_text(json.dumps(it, indent=1, ensure_ascii=False))
        except Exception as e:
            log.append(f"download {s}: {e}")

(OUT / "log.txt").write_text("\n".join(log))
print("\n".join(log))
