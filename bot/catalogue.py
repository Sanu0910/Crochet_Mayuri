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
    Category("bags", "👜 Bags", "Bags"),
    Category("garlands", "🌿 Garlands", "Garlands"),
    Category("hearts", "💗 Hearts", "Hearts"),
    Category("bookmarks", "📖 Bookmarks", "Bookmarks"),
    Category("coasters", "☕ Coasters", "Coasters"),
    Category("jewellery", "💍 Bangles", "Bangles"),
    # For a photo sent with no category: it still goes up under "Just in"
    # and can be moved later. No gallery filter of its own, on purpose.
    Category("new", "✨ New", "New"),
)

# Words in a name that settle the category when no hashtag was given.
KEYWORDS: tuple[tuple[str, str], ...] = (
    ("scrunchie", "scrunchies"), ("bow", "bows"), ("clip", "clips"),
    ("pin", "clips"), ("keychain", "keychains"), ("charm", "keychains"),
    ("bookmark", "bookmarks"), ("coaster", "coasters"), ("bangle", "jewellery"), ("bracelet", "jewellery"),
    ("band", "clips"), ("bag", "bags"), ("garland", "garlands"), ("heart", "hearts"),
    ("rose", "flowers"), ("flower", "flowers"), ("daisy", "flowers"),
    ("sunflower", "flowers"), ("bouquet", "flowers"),
)


def guess_category(text: str) -> str:
    """The category a name points to, or 'new' when nothing matches."""
    low = text.lower()
    for word, key in KEYWORDS:
        if word in low:
            return key
    return "new"

BY_KEY = {c.key: c for c in CATEGORIES}

# Every product gets a code: MZ-<group>-<number>, e.g. MZ-SCR-007. The group
# is the product type shown on the card ("shows under"), so pieces of the
# same type share a price group in the price list. Numbers only ever go up,
# so a code is never reused after a piece is removed.
SKU_PREFIX = "MZ"
GROUP_CODES: dict[str, str] = {
    "Scrunchies": "SCR",
    "Bows": "BOW",
    "Claw Clips": "CLW",
    "Hair Clips": "HCL",
    "Hair Pins": "HPN",
    "Hair Bands": "HBD",
    "Roses": "ROS",
    "Flowers": "FLW",
    "Keychains": "KEY",
    "Charms": "CHM",
    "Bags": "BAG",
    "Garlands": "GAR",
    "Hearts": "HRT",
    "Bookmarks": "BMK",
    "Coasters": "CST",
    "Bangles": "BNG",
    "New": "NEW",
}


def group_code(tag: str) -> str:
    return GROUP_CODES.get(tag, "NEW")
