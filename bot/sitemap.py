"""sitemap.xml with every product photo, so Google Images can find them.

The gallery is drawn by JavaScript, so the photos aren't in the page's HTML.
An image sitemap lists each one with its name. It's rebuilt from the PRODUCTS
list whenever the bot commits (repo.Repo.commit_and_push) and can be run by hand:

    py bot/sitemap.py            # from the repo root

`lastmod` only moves when the list of photos actually changes.
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

SITE = "https://mayurisyarntales.online/"
PRIVACY_LASTMOD = "2026-11-14"


def products(index_html: str) -> list[tuple[str, str, str]]:
    block = index_html.split("/* PRODUCTS:START */")[1].split("/* PRODUCTS:END */")[0]
    out = []
    for entry in block.split("{")[1:]:
        entry = entry.split("}")[0]

        def field(k: str) -> str:
            m = re.search(k + r":\s*'((?:[^'\\]|\\.)*)'", entry)
            return re.sub(r"\\(.)", r"\1", m.group(1)) if m else ""
        if field("image"):
            out.append((field("image"), field("name"), field("tag")))
    return out


def render(root: Path, home_lastmod: str, privacy_lastmod: str) -> str:
    items = products((root / "index.html").read_text(encoding="utf-8"))
    imgs = []
    for img, name, tag in items:
        title = name + (f" · handmade crochet {tag.lower()}" if tag and tag != "New" else "")
        imgs.append(f"    <image:image>\n      <image:loc>{escape(SITE + img)}</image:loc>\n"
                    f"      <image:title>{escape(title)}</image:title>\n    </image:image>\n")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
            f"  <url>\n    <loc>{SITE}</loc>\n    <lastmod>{home_lastmod}</lastmod>\n{''.join(imgs)}  </url>\n"
            f"  <url>\n    <loc>{SITE}privacy.html</loc>\n    <lastmod>{privacy_lastmod}</lastmod>\n  </url>\n"
            "</urlset>\n")


def build(root: Path) -> bool:
    """Rewrite sitemap.xml if the photo list changed. Returns True if it did."""
    path = root / "sitemap.xml"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    dates = re.findall(r"<lastmod>([\d-]+)</lastmod>", old)
    home = dates[0] if dates else ""
    privacy = dates[1] if len(dates) > 1 else PRIVACY_LASTMOD

    def strip(x: str) -> str:
        return re.sub(r"<lastmod>[^<]*</lastmod>", "", x)
    if old and strip(render(root, home, privacy)) == strip(old):
        return False
    path.write_text(render(root, dt.date.today().isoformat(), privacy), encoding="utf-8", newline="\n")
    return True


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    print("sitemap.xml updated" if build(root) else "sitemap.xml already up to date")
