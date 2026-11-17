"""One plain-HTML page per kind of piece, e.g. /crochet-scrunchies/.

The main page draws the gallery with JavaScript and covers everything at once,
so Google has no page that is *about* "crochet scrunchies" or "crochet gajra".
These pages are: own title, description and heading, the pieces as real HTML
(name, photo, description, an "Order this" link back to the order form), and
links to the other kinds. Built from the PRODUCTS list in index.html; called by
sitemap.build(), so the bot refreshes them on every commit. By hand:

    py bot/sitemap.py            # rebuilds these pages and the sitemap
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

SITE = "https://mayurisyarntales.online/"
EMAIL = "hello@mayurisyarntales.online"

# slug, product tags it covers, nav label, <h1>, <title>, meta description, intro
PAGES = [
    ("crochet-scrunchies", ["Scrunchies"], "Scrunchies",
     "Crochet Scrunchies", "Handmade Crochet Scrunchies | Mayuri's Yarn Tales",
     "Handmade crochet scrunchies by Mayuri: soft, gentle on hair and made to order in India, in any colour you like.",
     "Soft, comfy scrunchies crocheted by hand, gentle on your hair and easy to gift. Every one is made to order, "
     "so you can ask for any colour."),
    ("crochet-hair-ties", ["Hair Bands"], "Hair Ties",
     "Crochet Flower Hair Ties", "Crochet Flower Hair Ties & Hair Bands | Mayuri's Yarn Tales",
     "Handmade crochet flower hair ties and hair bands by Mayuri. A little bloom for your hair, made to order in India.",
     "A little bloom for your hair: crochet flower hair ties and hair bands, light and comfy, in bright or soft "
     "colours. Each one is made by hand to order."),
    ("crochet-hair-clips", ["Claw Clips", "Hair Clips", "Hair Pins"], "Hair Clips",
     "Crochet Claw Clips & Hair Clips", "Crochet Claw Clips, Hair Clips & Pins | Mayuri's Yarn Tales",
     "Handmade crochet claw clips, hair clips and hair pins with flowers, daisies and more, made to order in India.",
     "Claw clips, hair clips and pins dressed up with crochet flowers, daisies and little details, all made by hand "
     "to order."),
    ("crochet-bows", ["Bows"], "Bows",
     "Crochet Hair Bows", "Handmade Crochet Hair Bows | Mayuri's Yarn Tales",
     "Handmade crochet hair bows by Mayuri, classic and cute, made to order in India in any colour.",
     "Classic and cute crochet bows for your hair, made by hand to order in the colour you like."),
    ("crochet-flowers", ["Roses", "Flowers"], "Roses & Flowers",
     "Crochet Roses & Flower Bouquets", "Crochet Roses & Flower Bouquets | Mayuri's Yarn Tales",
     "Handmade crochet roses, sunflowers and flower bouquets that never wilt, made to order in India by Mayuri.",
     "Roses, sunflowers and bouquets that never wilt: crochet flowers made by hand, for gifts, desks and "
     "special days."),
    ("crochet-gajra-garlands", ["Garlands"], "Gajra & Garlands",
     "Crochet Gajra & Garlands", "Crochet Gajra & Garlands | Mayuri's Yarn Tales",
     "Handmade crochet gajra and garlands by Mayuri: jasmine buds and flowers that never wilt, made to order in India.",
     "A crochet gajra for your hair or a garland for your home, made by hand so the flowers never wilt."),
    ("crochet-keychains", ["Keychains", "Charms", "Hearts"], "Keychains & Charms",
     "Crochet Keychains & Bag Charms", "Crochet Keychains & Bag Charms | Mayuri's Yarn Tales",
     "Handmade crochet keychains, bag charms and hearts by Mayuri, cute little gifts made to order in India.",
     "Cute little keychains, bag charms and hearts, crocheted by hand: easy gifts for friends, family and yourself."),
    ("crochet-bookmarks", ["Bookmarks"], "Bookmarks",
     "Crochet Bookmarks", "Handmade Crochet Bookmarks | Mayuri's Yarn Tales",
     "Handmade crochet bookmarks by Mayuri, a sweet gift for book lovers, made to order in India.",
     "Crochet bookmarks made by hand, a sweet little gift for every book lover."),
    ("crochet-coasters", ["Coasters"], "Coasters",
     "Crochet Coasters", "Handmade Crochet Coasters | Mayuri's Yarn Tales",
     "Handmade crochet coasters by Mayuri, cosy home decor made to order in India in any colour.",
     "Cosy crochet coasters for your table, made by hand to order in the colours you like."),
    ("crochet-bangles", ["Bangles"], "Bangles",
     "Crochet Bangles", "Handmade Crochet Bangles | Mayuri's Yarn Tales",
     "Handmade crochet bangles by Mayuri, light and colourful, made to order in India.",
     "Light, colourful crochet bangles, made by hand to order."),
    ("crochet-bags", ["Bags"], "Bags",
     "Crochet Bags", "Handmade Crochet Bags | Mayuri's Yarn Tales",
     "Handmade crochet bags by Mayuri, made to order in India.",
     "Crochet bags made by hand to order, stitch by stitch."),
]


def products(index_html: str) -> list[dict]:
    block = index_html.split("/* PRODUCTS:START */")[1].split("/* PRODUCTS:END */")[0]
    out = []
    for entry in block.split("{")[1:]:
        entry = entry.split("}")[0]

        def field(k: str) -> str:
            m = re.search(k + r":\s*'((?:[^'\\]|\\.)*)'", entry)
            return re.sub(r"\\(.)", r"\1", m.group(1)) if m else ""
        p = {k: field(k) for k in ("id", "name", "tag", "desc", "image")}
        if p["id"] and p["image"]:
            out.append(p)
    return out


def live_pages(items: list[dict]) -> list[tuple]:
    """Pages that have at least one piece."""
    return [pg for pg in PAGES if any(p["tag"] in pg[1] for p in items)]


def render(page: tuple, items: list[dict], nav: list[tuple]) -> str:
    slug, tags, label, h1, title, desc, intro = page
    e = html.escape
    pieces = [p for p in items if p["tag"] in tags]
    url = f"{SITE}{slug}/"
    cards = "\n".join(
        f'    <li class="card">\n'
        f'      <img src="/{e(p["image"])}" alt="{e(p["name"])}, handmade crochet {e(p["tag"].lower())} '
        f'by Mayuri&#39;s Yarn Tales" loading="lazy" width="800" height="1000">\n'
        f'      <h2>{e(p["name"])}</h2>\n'
        f'      <p>{e(p["desc"])}</p>\n'
        f'      <a class="order" href="/?order={e(p["id"])}#order">Order this</a>\n'
        f'    </li>' for p in pieces)
    links = " ".join(
        f'<a href="/{pg[0]}/"' + (' aria-current="page"' if pg[0] == slug else "") + f">{e(pg[2])}</a>"
        for pg in nav)
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CollectionPage", "@id": url, "url": url, "name": h1, "description": desc,
             "inLanguage": "en-IN", "isPartOf": {"@id": f"{SITE}#website"},
             "about": {"@id": f"{SITE}#store"},
             "primaryImageOfPage": f"{SITE}{pieces[0]['image']}"},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Mayuri's Yarn Tales", "item": SITE},
                {"@type": "ListItem", "position": 2, "name": label, "item": url}]},
        ],
    }
    return f"""<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Made by bot/category_pages.py from the PRODUCTS list in index.html. Don't edit by hand. -->
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/media/icon.svg" type="image/svg+xml">
<meta property="og:site_name" content="Mayuri's Yarn Tales">
<meta property="og:title" content="{e(h1)} · Mayuri's Yarn Tales">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}{e(pieces[0]['image'])}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_IN">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
<style>
  :root{{--ink:#1d1d1f;--ink-soft:#4a4a4f;--accent:#c8564a;--surface:#fff;--surface-alt:#f9ece4;--line:rgba(0,0,0,.08)}}
  @media (prefers-color-scheme: dark){{:root{{--ink:#f5f5f7;--ink-soft:#c7c7cc;--surface:#1d1d1f;--surface-alt:#2c2c2e;--line:rgba(255,255,255,.12)}}}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--surface);color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Inter","Segoe UI",sans-serif}}
  main{{max-width:1080px;margin:0 auto;padding:28px 16px 64px}}
  a{{color:var(--accent)}}
  .back{{display:inline-flex;align-items:center;gap:8px;font-weight:600;text-decoration:none;color:var(--ink)}}
  h1{{font-size:clamp(1.8rem,5vw,2.6rem);line-height:1.15;margin:28px 0 8px}}
  .intro{{color:var(--ink-soft);max-width:640px;margin:0 0 20px}}
  nav{{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 28px}}
  nav a{{text-decoration:none;color:var(--ink);border:1px solid var(--line);border-radius:999px;padding:6px 14px;font-size:.9rem}}
  nav a[aria-current]{{background:var(--ink);color:var(--surface);border-color:var(--ink)}}
  ul{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:16px}}
  .card{{background:var(--surface-alt);border-radius:18px;overflow:hidden;display:flex;flex-direction:column}}
  .card img{{width:100%;height:auto;aspect-ratio:4/5;object-fit:contain;display:block}}
  .card h2{{font-size:1rem;margin:12px 14px 4px}}
  .card p{{color:var(--ink-soft);font-size:.9rem;margin:0 14px 12px;flex:1}}
  .order{{margin:0 14px 14px;align-self:flex-start;background:var(--accent);color:#fff;text-decoration:none;font-weight:600;font-size:.88rem;border-radius:999px;padding:8px 14px}}
  .more{{margin-top:40px;color:var(--ink-soft)}}
  @media (min-width:700px){{ul{{grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:20px}}}}
</style>
</head>
<body>
<main>
  <a class="back" href="/"><img src="/media/icon.svg" alt="" width="24" height="24">Mayuri's Yarn Tales</a>
  <h1>{e(h1)}</h1>
  <p class="intro">{e(intro)} Handmade by Mayuri in India.</p>
  <nav aria-label="Shop by kind">{links}</nav>
  <ul>
{cards}
  </ul>
  <p class="more">Want a different colour or something custom? <a href="/#order">Tell us on the order form</a>
  or email <a href="mailto:{EMAIL}">{EMAIL}</a>. <a href="/#gallery">See the whole collection</a>.</p>
</main>
</body>
</html>
"""


def build(root: Path) -> dict[str, bool]:
    """Write every category page. Returns {slug: changed} for pages that exist.
    Removes a page whose kind has no pieces left."""
    items = products((root / "index.html").read_text(encoding="utf-8"))
    nav = live_pages(items)
    out = {}
    for page in PAGES:
        path = root / page[0] / "index.html"
        if page not in nav:
            if path.exists():
                path.unlink()
                path.parent.rmdir()
            continue
        new = render(page, items, nav)
        # the bot's clone checks files out with CRLF; compare content, not line endings
        old = path.read_text(encoding="utf-8").replace("\r\n", "\n") if path.exists() else ""
        out[page[0]] = new != old
        if new != old:
            path.parent.mkdir(exist_ok=True)
            path.write_text(new, encoding="utf-8", newline="\n")
    return out
