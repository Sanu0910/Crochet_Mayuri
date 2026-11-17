"""sitemap.xml with every page and every product photo, for Google.

The gallery is drawn by JavaScript, so the photos aren't in the page's HTML.
An image sitemap lists each one with its name. This also (re)builds the
category pages (bot/category_pages.py) and lists them. It runs whenever the
bot commits (tools/run-bot.ps1, repo.Repo.commit_and_push) and by hand:

    py bot/sitemap.py            # from the repo root

Each page's `lastmod` only moves when that page actually changes.
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import category_pages  # noqa: E402

SITE = "https://mayurisyarntales.online/"
PRIVACY_LASTMOD = "2026-11-14"
IMG_RE = re.compile(r"<image:image>.*?</image:image>", re.S)


def render(root: Path, lastmods: dict[str, str]) -> str:
    """lastmods: {page url: YYYY-MM-DD}; the home page carries the photos."""
    items = category_pages.products((root / "index.html").read_text(encoding="utf-8"))
    imgs = []
    for p in items:
        title = p["name"] + (f" · handmade crochet {p['tag'].lower()}" if p["tag"] and p["tag"] != "New" else "")
        imgs.append(f"    <image:image>\n      <image:loc>{escape(SITE + p['image'])}</image:loc>\n"
                    f"      <image:title>{escape(title)}</image:title>\n    </image:image>\n")
    urls = [f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{mod}</lastmod>\n"
            f"{''.join(imgs) if loc == SITE else ''}  </url>\n" for loc, mod in lastmods.items()]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
            + "".join(urls) + "</urlset>\n")


def build(root: Path) -> bool:
    """Rebuild the category pages and sitemap.xml. Returns True if anything changed."""
    today = dt.date.today().isoformat()
    pages = category_pages.build(root)          # {slug: changed}
    path = root / "sitemap.xml"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    old_mods = dict(re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", old))

    mods = {SITE: old_mods.get(SITE, today)}
    for slug, changed in pages.items():
        loc = f"{SITE}{slug}/"
        mods[loc] = today if changed or loc not in old_mods else old_mods[loc]
    mods[f"{SITE}privacy.html"] = old_mods.get(f"{SITE}privacy.html", PRIVACY_LASTMOD)
    new = render(root, mods)
    if IMG_RE.findall(new) != IMG_RE.findall(old):   # photo list changed -> home changed
        mods[SITE] = today
        new = render(root, mods)
    if new == old:
        return any(pages.values())
    path.write_text(new, encoding="utf-8", newline="\n")
    return True


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    print("sitemap + category pages updated" if build(root) else "already up to date")
