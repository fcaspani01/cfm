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
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "public"

SITE = {
    # TODO: sostituire con il dominio definitivo prima della messa online
    "url": "https://www.cfmassistenzacaldaie.it",
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


def fill(text):
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
    return fill(page)


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
            (OUT / name).write_text(fill(p.read_text(encoding="utf-8")), encoding="utf-8")

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
