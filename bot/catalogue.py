"""Shared knowledge about the shop's catalogue.

Mirrors the CATEGORIES list in index.html. If a category is added there,
add it here too or the bot won't offer it.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    key: str      # the `cat` field on a product, and the gallery filter key
    button: str   # what the Telegram button says
    tag: str      # the small label printed on the product card


CATEGORIES: tuple[Category, ...] = (
    Category("scrunchies", "🌸 Scrunchies", "Scrunchies"),
    Category("bows", "🎀 Bows", "Bows"),
    Category("flowers", "🌹 Flowers & Roses", "Roses"),
    Category("clips", "📎 Clips", "Hair Clips"),
    Category("keychains", "🔑 Keychains", "Keychains"),
    Category("garlands", "🌿 Garlands", "Garlands"),
    Category("hearts", "💗 Hearts", "Hearts"),
)

BY_KEY = {c.key: c for c in CATEGORIES}
