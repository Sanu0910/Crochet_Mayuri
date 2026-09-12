"""Inserting a product into the site and into the film's scene list.

Both files keep their product list between `PRODUCTS:START` and
`PRODUCTS:END` markers. New entries are placed just before the first
existing entry in the same category so the gallery stays grouped; if the
category has no entries yet, the new one goes at the end of the list.
"""

import re
from pathlib import Path

from catalogue import BY_KEY

START = "PRODUCTS:START"
END = "PRODUCTS:END"


class SiteEditError(RuntimeError):
    pass


def _js_string(value: str) -> str:
    """Escape a value for a single-quoted JS string literal.

    The `</` guard matters: this string ends up inside a <script> block in
    index.html, and a caption containing "</script>" would otherwise close
    the block and break the whole page.
    """
    return (
        value.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("</", "<\\/")
        .replace("\n", " ")
    )


def _marker_span(text: str, path: Path) -> tuple[int, int]:
    start = text.find(START)
    end = text.find(END)
    if start == -1 or end == -1 or end < start:
        raise SiteEditError(
            f"{path.name} is missing its {START}/{END} markers — "
            "the bot can't safely edit it. See bot/README.md."
        )
    # Insert inside the block: after the line carrying START, before the
    # line carrying END.
    return text.index("\n", start) + 1, text.rindex("\n", 0, end) + 1


def product_ids(index_html: str) -> list[str]:
    return re.findall(r"^\s*id: '([^']+)'", index_html, re.MULTILINE)


def insert_into_index(
    path: Path, *, product_id: str, name: str, cat: str, desc: str, image: str
) -> None:
    text = path.read_text()
    if f"id: '{product_id}'" in text:
        raise SiteEditError(f"a product with the id '{product_id}' already exists")

    category = BY_KEY[cat]
    entry = (
        f"    {{\n"
        f"      id: '{_js_string(product_id)}',\n"
        f"      name: '{_js_string(name)}',\n"
        f"      cat: '{cat}', tag: '{_js_string(category.tag)}', badge: 'New',\n"
        f"      desc: '{_js_string(desc)}',\n"
        f"      image: 'images/{image}'\n"
        f"    }},\n"
    )

    block_start, block_end = _marker_span(text, path)
    block = text[block_start:block_end]

    # Sit with the rest of the category if it already has members.
    match = re.search(r"^    \{\n(?:.*\n)*?.*cat: '%s'.*$" % re.escape(cat), block, re.MULTILINE)
    if match:
        # Walk back to the opening brace of that entry.
        entry_start = block.rindex("    {\n", 0, match.end())
        at = block_start + entry_start
    else:
        at = block_end

    path.write_text(text[:at] + entry + text[at:])


def insert_into_film(path: Path, *, name: str, cat: str, image: str) -> None:
    """Keep video/src/theme.ts in step, so the next render includes the piece."""
    text = path.read_text()
    category = BY_KEY[cat]
    entry = (
        f'  {{ image: "{image}", '
        f'name: {_ts_string(name)}, '
        f'tag: "{category.tag}" }},\n'
    )

    block_start, block_end = _marker_span(text, path)
    block = text[block_start:block_end]

    match = re.search(r'^  \{ image: .*tag: "%s" \},$' % re.escape(category.tag),
                      block, re.MULTILINE)
    if match:
        at = block_start + block.rindex("  { image:", 0, match.end())
    else:
        at = block_end

    path.write_text(text[:at] + entry + text[at:])


def _ts_string(value: str) -> str:
    """TypeScript double-quoted string."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'


def remove_product(
    index_path: Path, theme_path: Path, images_dir: Path, query: str
) -> tuple[str, str]:
    """Take a piece off the site again. Returns (name, image file name).

    Deleting the wrong piece is the one mistake here that loses work, so
    matching is deliberately cautious: an exact id or name wins outright, and
    a partial name is only accepted when it picks out exactly one piece.
    "priced" must not quietly match "Unpriced Bow".
    """
    text = index_path.read_text()
    entries = re.findall(r"    \{\n(?:.*\n)*?    \},\n", text)

    found = []
    for entry in entries:
        product_id = re.search(r"id: '([^']+)'", entry)
        name = re.search(r"name: '([^']+)'", entry)
        image = re.search(r"image: 'images/([^']+)'", entry)
        if product_id and name and image:
            found.append((entry, product_id.group(1), name.group(1), image.group(1)))

    needle = " ".join(query.split()).lower()
    exact = [f for f in found if needle in (f[1].lower(), f[2].lower())]
    partial = [f for f in found if needle in f[2].lower() or needle in f[1].lower()]

    if exact:
        matches = exact
    elif len(partial) > 1:
        names = ", ".join(f"\u201c{f[2]}\u201d" for f in partial[:5])
        raise SiteEditError(
            f"\u201c{query}\u201d matches {len(partial)} pieces ({names}). "
            "Use the full name so I remove the right one."
        )
    else:
        matches = partial

    if not matches:
        raise SiteEditError(
            f"I couldn't find a piece matching \u201c{query}\u201d. "
            "Use the exact name, or the id shown when it was added."
        )

    entry, _, name, image = matches[0]
    index_path.write_text(text.replace(entry, "", 1))

    theme = theme_path.read_text()
    theme_line = re.search(r'^  \{ image: "%s".*\},\n' % re.escape(image),
                           theme, re.MULTILINE)
    if theme_line:
        theme_path.write_text(theme.replace(theme_line.group(0), "", 1))

    photo = images_dir / image
    if photo.exists():
        photo.unlink()

    return name, image


def _find_entry(text: str, query: str) -> tuple[str, str, str, str]:
    """Locate one product entry. Same cautious matching as remove_product."""
    entries = re.findall(r"    \{\n(?:.*\n)*?    \},\n", text)
    found = []
    for entry in entries:
        product_id = re.search(r"id: '([^']+)'", entry)
        name = re.search(r"name: '([^']+)'", entry)
        image = re.search(r"image: 'images/([^']+)'", entry)
        if product_id and name and image:
            found.append((entry, product_id.group(1), name.group(1), image.group(1)))

    needle = " ".join(query.split()).lower()
    exact = [f for f in found if needle in (f[1].lower(), f[2].lower())]
    partial = [f for f in found if needle in f[2].lower() or needle in f[1].lower()]

    if exact:
        return exact[0]
    if len(partial) > 1:
        names = ", ".join(f"\u201c{f[2]}\u201d" for f in partial[:5])
        raise SiteEditError(
            f"\u201c{query}\u201d matches {len(partial)} pieces ({names}). "
            "Use the full name."
        )
    if partial:
        return partial[0]
    raise SiteEditError(f"I couldn't find a piece matching \u201c{query}\u201d.")


def update_product(
    index_path: Path, theme_path: Path, query: str, *,
    name: str | None = None, desc: str | None = None
) -> tuple[str, str]:
    """Change a piece's displayed name or description. Returns (old, new) name.

    The id and the photo file are left alone deliberately: they are what the
    gallery, the film and any link already point at, and renaming them to
    follow a wording change would break more than it tidies.
    """
    text = index_path.read_text()
    entry, _, old_name, image = _find_entry(text, query)

    updated = entry
    if name:
        updated = re.sub(r"(name: ')[^']*(')", lambda m: m.group(1) + _js_string(name) + m.group(2),
                         updated, count=1)
    if desc:
        updated = re.sub(r"(desc: ')[^']*(')", lambda m: m.group(1) + _js_string(desc) + m.group(2),
                         updated, count=1)
    index_path.write_text(text.replace(entry, updated, 1))

    if name:
        theme = theme_path.read_text()
        line = re.search(r'^  \{ image: "%s", name: "[^"]*"' % re.escape(image),
                         theme, re.MULTILINE)
        if line:
            # The match runs from the start of the line through the closing
            # quote of the old name, so the replacement rebuilds exactly that.
            replacement = f'  {{ image: "{image}", name: {_ts_string(name)}'
            theme_path.write_text(theme.replace(line.group(0), replacement, 1))

    return old_name, (name or old_name)
