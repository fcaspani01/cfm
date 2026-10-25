#!/usr/bin/env python3
"""Genera il sito statico in public/ a partire da src/.

Uso:  python3 build.py
Nessuna dipendenza esterna: solo libreria standard.

Tutti i dati aziendali (NAP, orari, dominio) stanno in SITE qui sotto:
cambiarli qui li aggiorna in ogni pagina, nel JSON-LD, in llms.txt e nella sitemap.
"""
import datetime
import html
import json
import re
import os
import shutil
from urllib.parse import urlparse
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "public"

SITE = {
    # URL pubblico del sito, senza "/" finale. Ora è GitHub Pages; con un dominio proprio
    # basta cambiarlo qui (o con la variabile d'ambiente SITE_URL) e rigenerare.
    "url": os.environ.get("SITE_URL", "https://fcaspani01.github.io/cfm").rstrip("/"),
    "name": "CFM Centro Assistenza Caldaie Vaillant Verona",
    "short_name": "CFM Assistenza Caldaie",
    "legal_name": "CFM S.n.c. di Caspani M., Faustini G., Mirandola R.",
    "phone": "045 875 1000",
    "phone_e164": "+390458751000",
    "email": "cfmsnc1@virgilio.it",
    "street": "Via Cesare Battisti, 58",
    "postal_code": "37057",
    "city": "San Giovanni Lupatoto",
    "province": "VR",
    "region": "Veneto",
    "country": "IT",
    "lat": 45.3830,
    "lng": 11.0440,
    # TODO: verificare gli orari reali (le directory online riportano dati discordanti)
    "hours": [
        {"days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
         "label": "Lunedì – Venerdì", "opens": "07:30", "closes": "18:30"},
    ],
    "hours_closed_label": "Sabato e domenica",
    "experience_years": "40",
    "vat": "",  # TODO: inserire la Partita IVA (obbligatoria nel footer per legge)
    "maps_url": "https://www.google.com/maps/search/?api=1&query=CFM+Vaillant+Via+Cesare+Battisti+58+San+Giovanni+Lupatoto",
    # TODO: incollare il link della scheda Google Business Profile (es. https://g.page/r/...)
    "gbp_url": "https://share.google/6DwVYnbNmBD4MdLbm",
    "areas": [
        "Verona", "San Giovanni Lupatoto", "San Martino Buon Albergo", "Zevio",
        "Castel d'Azzano", "Buttapietra", "Vigasio", "Villafranca di Verona",
        "Oppeano", "Isola della Scala", "Povegliano Veronese", "Sommacampagna",
        "Bussolengo", "Pescantina", "Lavagno", "Caldiero", "Belfiore",
        "Ronco all'Adige", "Palù", "Grezzana", "Negrar di Valpolicella",
    ],
}

NAV = [
    ("/", "Home"),
    ("/assistenza-caldaie-vaillant-verona/", "Assistenza Vaillant"),
    ("/manutenzione-caldaia-verona/", "Manutenzione"),
    ("/riparazione-caldaie-verona/", "Riparazioni"),
    ("/sostituzione-caldaia-verona/", "Sostituzione"),
    ("/zone-servite/", "Zone"),
    ("/chi-siamo/", "Chi siamo"),
    ("/faq/", "FAQ"),
    ("/contatti/", "Contatti"),
]

# Sottopercorso del sito (es. "/cfm" su GitHub Pages), ricavato dall'URL
BASE = urlparse(SITE["url"]).path.rstrip("/")
SRCSET_RE = re.compile(r'srcset="([^"]*)"')
ROOT_LINK_RE = re.compile(r'((?:href|src|action)=")/(?!/)')


def with_base(text):
    """Antepone BASE ai link che iniziano con "/" (no-op se il sito è alla radice del dominio)."""
    if not BASE:
        return text
    text = ROOT_LINK_RE.sub(lambda m: m.group(1) + BASE + "/", text)
    # srcset: elenco "url larghezza, url larghezza"
    return SRCSET_RE.sub(lambda m: 'srcset="' + re.sub(r"(^|,\s*)/(?!/)", lambda n: n.group(1) + BASE + "/", m.group(1)) + '"', text)


META_RE = re.compile(r"^\s*<!--meta\s*(\{.*?\})\s*-->", re.S)


def tokens():
    s = SITE
    hours_text = "; ".join(f"{h['label']} {h['opens']}–{h['closes']}" for h in s["hours"])
    return {
        "PHONE": s["phone"],
        "PHONE_LINK": "tel:" + s["phone_e164"],
        "EMAIL": s["email"],
        "STREET": s["street"],
        "POSTAL_CODE": s["postal_code"],
        "CITY": s["city"],
        "PROVINCE": s["province"],
        "ADDRESS": f"{s['street']}, {s['postal_code']} {s['city']} ({s['province']})",
        "LEGAL_NAME": s["legal_name"],
        "NAME": s["name"],
        "YEARS": s["experience_years"],
        "HOURS": hours_text,
        "HOURS_CLOSED": s["hours_closed_label"],
        "MAPS_URL": s["maps_url"],
        "GBP_URL": s["gbp_url"],
        "SITE_URL": s["url"],
        "AREAS_LIST": ", ".join(s["areas"]),
        "AREAS_HTML": "".join(f"<li>{html.escape(a)}</li>" for a in s["areas"]),
        "YEAR": str(datetime.date.today().year),
        "VAT": s["vat"] or "[P.IVA da inserire]",
    }


# Coordinate approssimate dei comuni, usate solo per disegnare la mappa schematica delle zone
COORDS = {
    "Verona": (45.4384, 10.9916), "San Giovanni Lupatoto": (45.3833, 11.0433),
    "San Martino Buon Albergo": (45.4206, 11.0960), "Zevio": (45.3722, 11.1306),
    "Castel d'Azzano": (45.3533, 10.9536), "Buttapietra": (45.3433, 10.9969),
    "Vigasio": (45.3175, 10.9425), "Villafranca di Verona": (45.3540, 10.8447),
    "Oppeano": (45.3047, 11.1792), "Isola della Scala": (45.2714, 10.9858),
    "Povegliano Veronese": (45.3483, 10.8806), "Sommacampagna": (45.4053, 10.8467),
    "Bussolengo": (45.4747, 10.8506), "Pescantina": (45.4847, 10.8681),
    "Lavagno": (45.4378, 11.1336), "Caldiero": (45.4153, 11.1803),
    "Belfiore": (45.3814, 11.2097), "Ronco all'Adige": (45.3369, 11.2436),
    "Palù": (45.3247, 11.1556), "Grezzana": (45.5197, 11.0158),
    "Negrar di Valpolicella": (45.5289, 10.9389),
}
# Corso dell'Adige semplificato (nord-ovest -> sud-est)
ADIGE = [(45.53, 10.80), (45.50, 10.85), (45.485, 10.90), (45.465, 10.955), (45.448, 10.985),
         (45.443, 11.005), (45.432, 11.012), (45.428, 11.035), (45.410, 11.060), (45.385, 11.085),
         (45.368, 11.125), (45.350, 11.180), (45.330, 11.240), (45.315, 11.27)]
# Etichette da mettere a sinistra del punto per evitare sovrapposizioni
LEFT_LABELS = {"Villafranca di Verona", "Sommacampagna", "Bussolengo", "Povegliano Veronese",
               "Negrar di Valpolicella", "Vigasio"}
# Spostamenti verticali delle etichette troppo vicine
LABEL_DY = {"San Martino Buon Albergo": -10, "Caldiero": 6, "Povegliano Veronese": 10,
            "Villafranca di Verona": -6, "Castel d'Azzano": -10, "Belfiore": -6}


def zone_map():
    """Mappa SVG schematica: sede, comuni serviti, Adige e cerchi di distanza."""
    # Proiezione adattata ai comuni in elenco, con margini per le etichette
    pts = [COORDS[a] for a in SITE["areas"] if a in COORDS]
    lat_min, lat_max = min(p[0] for p in pts), max(p[0] for p in pts)
    lng_min, lng_max = min(p[1] for p in pts), max(p[1] for p in pts)
    W, pad_l, pad_r, pad_y = 760, 180, 120, 40
    k = (W - pad_l - pad_r) / ((lng_max - lng_min) * 0.70)
    H = round((lat_max - lat_min) * k + 2 * pad_y)
    proj = lambda lat, lng: (pad_l + (lng - lng_min) * k * 0.70, pad_y + (lat_max - lat) * k)
    sx, sy = proj(*COORDS["San Giovanni Lupatoto"])
    km = k / 111  # pixel per km (in verticale)
    river = " ".join(f"{x:.0f},{y:.0f}" for x, y in (proj(*p) for p in ADIGE))
    parts = [
        f'<svg class="zone-map" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Mappa schematica dei comuni serviti attorno a San Giovanni Lupatoto e Verona">',
        f'<rect width="{W}" height="{H}" rx="18" fill="var(--map-bg)"/>',
    ]
    for r, lbl in ((10, "10 km"), (20, "20 km")):
        parts.append(f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="{r*km:.0f}" fill="none" stroke="var(--brand)" '
                     f'stroke-opacity=".28" stroke-dasharray="6 6"/>')
        parts.append(f'<text x="{sx + r*km*0.71 + 4:.0f}" y="{sy - r*km*0.71:.0f}" class="zm-km">{lbl}</text>')
    parts.append(f'<polyline points="{river}" fill="none" stroke="#7cc3e0" stroke-width="7" '
                 f'stroke-linecap="round" stroke-linejoin="round" opacity=".7"/>')
    rx, ry = proj(45.300, 11.21)
    parts.append(f'<text x="{rx:.0f}" y="{ry + 22:.0f}" class="zm-river">fiume Adige</text>')
    for name in SITE["areas"]:
        if name not in COORDS or name == "San Giovanni Lupatoto":
            continue
        x, y = proj(*COORDS[name])
        big = name == "Verona"
        parts.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{9 if big else 5}" fill="var(--brand-2)"/>')
        anchor, dx = ("end", -10) if name in LEFT_LABELS else ("start", 10)
        dy = LABEL_DY.get(name, 0)
        cls = "zm-city zm-big" if big else "zm-city"
        parts.append(f'<text x="{x + dx:.0f}" y="{y + 4 + dy:.0f}" text-anchor="{anchor}" class="{cls}">'
                     f'{html.escape(name)}</text>')
    parts.append(f'<g transform="translate({sx:.0f},{sy:.0f})">'
                 '<circle r="26" fill="var(--accent)" opacity=".18"/>'
                 '<path d="M0 6c-7-8-12-13-12-19a12 12 0 0 1 24 0c0 6-5 11-12 19z" fill="var(--accent)"/>'
                 '<circle cy="-13" r="4.5" fill="#fff"/></g>')
    parts.append(f'<text x="{sx:.0f}" y="{sy - 34:.0f}" text-anchor="middle" class="zm-hq">CFM · San Giovanni Lupatoto</text>')
    parts.append("</svg>")
    return "".join(parts)


def icon(name):
    svg = (SRC / "icons" / f"{name}.svg").read_text(encoding="utf-8")
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r'\s*class="[^"]*"', "", svg)
    svg = svg.replace("<svg", '<svg class="ico" aria-hidden="true" focusable="false"', 1)
    return re.sub(r"\s+", " ", svg).replace("> <", "><").strip()


def fill(text):
    text = re.sub(r"\{\{ICON:([a-z-]+)\}\}", lambda m: icon(m.group(1)), text)
    text = re.sub(r"\{\{SVG:([a-z-]+)\}\}",
                  lambda m: (SRC / "illustrations" / f"{m.group(1)}.svg").read_text(encoding="utf-8").strip(), text)
    if "{{ZONE_MAP}}" in text:
        text = text.replace("{{ZONE_MAP}}", zone_map())
    for k, v in tokens().items():
        text = text.replace("{{" + k + "}}", v)
    return text


def business_schema():
    s = SITE
    return {
        "@context": "https://schema.org",
        "@type": ["HVACBusiness", "LocalBusiness"],
        "@id": s["url"] + "/#business",
        "name": s["name"],
        "alternateName": [
            "CFM S.n.c.", "Centro Assistenza CFM",
            "Vaillant Service Centro Assistenza CFM",
            s["legal_name"],
        ],
        "legalName": s["legal_name"],
        "description": (
            f"Centro assistenza caldaie a San Giovanni Lupatoto (Verona) con oltre "
            f"{s['experience_years']} anni di esperienza, specializzato in caldaie Vaillant: "
            "manutenzione, controllo fumi, riparazioni, ricambi originali e sostituzione caldaia "
            "a Verona e provincia."
        ),
        "url": s["url"] + "/",
        "telephone": s["phone_e164"],
        "email": s["email"],
        "image": s["url"] + "/assets/og-image.png",
        "logo": s["url"] + "/assets/logo.svg",
        "priceRange": "€€",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": s["street"],
            "postalCode": s["postal_code"],
            "addressLocality": s["city"],
            "addressRegion": s["province"],
            "addressCountry": s["country"],
        },
        "geo": {"@type": "GeoCoordinates", "latitude": s["lat"], "longitude": s["lng"]},
        "hasMap": s["maps_url"],
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": h["days"],
             "opens": h["opens"], "closes": h["closes"]} for h in s["hours"]
        ],
        "areaServed": [{"@type": "City", "name": a} for a in s["areas"]]
        + [{"@type": "AdministrativeArea", "name": "Provincia di Verona"}],
        "knowsAbout": [
            "Caldaie Vaillant", "Caldaie a condensazione", "Vaillant ecoTEC",
            "Manutenzione caldaie", "Controllo fumi", "Rapporto di efficienza energetica",
            "Libretto di impianto", "Riparazione caldaie", "Codici errore Vaillant",
            "Sostituzione caldaia", "Scaldabagni a gas",
        ],
        "brand": {"@type": "Brand", "name": "Vaillant"},
        "slogan": "Assistenza caldaie Vaillant a Verona da oltre 40 anni",
        "sameAs": [u for u in [s["gbp_url"]] if u],
        "makesOffer": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "url": s["url"] + p}}
            for n, p in [
                ("Assistenza caldaie Vaillant", "/assistenza-caldaie-vaillant-verona/"),
                ("Manutenzione caldaia e controllo fumi", "/manutenzione-caldaia-verona/"),
                ("Riparazione caldaie", "/riparazione-caldaie-verona/"),
                ("Sostituzione e installazione caldaia", "/sostituzione-caldaia-verona/"),
            ]
        ],
    }


def website_schema():
    s = SITE
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": s["url"] + "/#website",
        "url": s["url"] + "/",
        "name": s["name"],
        "inLanguage": "it-IT",
        "publisher": {"@id": s["url"] + "/#business"},
    }


def breadcrumb_schema(path, title):
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE["url"] + "/"}]
    if path != "/":
        items.append({"@type": "ListItem", "position": 2, "name": title, "item": SITE["url"] + path})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def faq_schema(body):
    """Estrae le FAQ marcate <details class="faq"> per il JSON-LD FAQPage."""
    pairs = re.findall(
        r'<details class="faq"[^>]*>\s*<summary>(.*?)</summary>\s*(.*?)</details>', body, re.S
    )
    if not pairs:
        return None
    strip = lambda t: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t)).strip()
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": strip(q),
             "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
            for q, a in pairs
        ],
    }


def service_schema(meta):
    if "service" not in meta:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": meta["service"],
        "serviceType": meta["service"],
        "description": meta["description"],
        "provider": {"@id": SITE["url"] + "/#business"},
        "areaServed": {"@type": "AdministrativeArea", "name": "Provincia di Verona"},
        "url": SITE["url"] + meta["path"],
    }


def render_nav(current):
    out = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == current else ""
        out.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    return "\n".join(out)


def render_page(meta, body, layout):
    path = meta["path"]
    canonical = SITE["url"] + path
    schemas = [business_schema(), website_schema(), breadcrumb_schema(path, meta.get("crumb", meta["h1"]))]
    for extra in (service_schema(meta), faq_schema(body)):
        if extra:
            schemas.append(extra)
    ld = "\n".join(
        f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>'
        for x in schemas
    )
    page = layout
    page = page.replace("{{TITLE}}", html.escape(meta["title"]))
    page = page.replace("{{DESCRIPTION}}", html.escape(meta["description"]))
    page = page.replace("{{CANONICAL}}", canonical)
    page = page.replace("{{ROBOTS}}", meta.get("robots", "index, follow, max-image-preview:large, max-snippet:-1"))
    page = page.replace("{{JSONLD}}", ld)
    page = page.replace("{{NAV}}", render_nav(path))
    page = page.replace("{{CONTENT}}", body)
    return with_base(fill(page))


def html_to_text(body):
    """Versione testuale semplice di una pagina, per llms-full.txt."""
    t = re.sub(r"<(script|style|form|iframe)[^>]*>.*?</\1>", "", body, flags=re.S)
    t = re.sub(r"<h1[^>]*>(.*?)</h1>", r"\n# \1\n", t, flags=re.S)
    t = re.sub(r"<h2[^>]*>(.*?)</h2>", r"\n## \1\n", t, flags=re.S)
    t = re.sub(r"<h3[^>]*>(.*?)</h3>", r"\n### \1\n", t, flags=re.S)
    t = re.sub(r"<summary>(.*?)</summary>", r"\n### \1\n", t, flags=re.S)
    t = re.sub(r"<li[^>]*>", "\n- ", t)
    t = re.sub(r"<(br|/p|/dd)\s*/?>", "\n", t)
    t = re.sub(r"<dt[^>]*>", "\n- **", t)
    t = re.sub(r"</dt>", "**: ", t)
    t = re.sub(r"<t[dh](\s[^>]*)?>", "| ", t)
    t = re.sub(r"</t[dh]>", " ", t)
    t = re.sub(r"</tr>", "|\n", t)
    t = t.replace("</thead>", "|---|---|---|\n")
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t)
    t = re.sub(r"\|\n\s*\n(?=\s*\|)", "|\n", t)
    return "\n".join(line.strip() for line in t.splitlines()).strip()


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(SRC / "assets", OUT / "assets")
    layout = (SRC / "layout.html").read_text(encoding="utf-8")

    pages = []
    for f in sorted((SRC / "pages").glob("*.html")):
        raw = f.read_text(encoding="utf-8")
        m = META_RE.match(raw)
        if not m:
            raise SystemExit(f"{f}: manca il blocco <!--meta {{...}} -->")
        meta = json.loads(m.group(1))
        body = fill(raw[m.end():])
        out_html = render_page(meta, body, layout)
        dest = OUT / meta["path"].strip("/") / "index.html" if meta["path"].endswith("/") \
            else OUT / meta["path"].lstrip("/")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out_html, encoding="utf-8")
        pages.append((meta, body))

    for name in ("robots.txt", "llms.txt", "_headers", "site.webmanifest"):
        p = SRC / name
        if p.exists():
            text = fill(p.read_text(encoding="utf-8"))
            if name == "site.webmanifest" and BASE:
                text = re.sub(r'": "/', '": "' + BASE + "/", text)
            (OUT / name).write_text(text, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    today = datetime.date.today().isoformat()
    indexable = [m for m, _ in pages if "noindex" not in m.get("robots", "")]
    urls = "\n".join(
        f"  <url><loc>{SITE['url']}{m['path']}</loc><lastmod>{today}</lastmod>"
        f"<priority>{m.get('priority', '0.7')}</priority></url>"
        for m in indexable
    )
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n",
        encoding="utf-8",
    )

    full = [fill((SRC / "llms.txt").read_text(encoding="utf-8")), "\n\n---\n"]
    for m, body in pages:
        if "noindex" in m.get("robots", ""):
            continue
        full.append(f"\n\n<!-- Fonte: {SITE['url']}{m['path']} -->\n")
        full.append(html_to_text(body))
    (OUT / "llms-full.txt").write_text("".join(full) + "\n", encoding="utf-8")

    print(f"OK: {len(pages)} pagine generate in {OUT}")


if __name__ == "__main__":
    main()
