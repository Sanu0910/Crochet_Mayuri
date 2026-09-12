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
