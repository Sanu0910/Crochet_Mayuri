"""Spotting a price in a Telegram caption so it can be kept out of the name.

The site deliberately shows no prices — every piece is meant to start a
conversation instead. But captions get typed out of habit, and a caption
reading "Ocean Blue Scrunchie \u20b9250" must not become a product called
"Ocean Blue Scrunchie \u20b9250". So a price is still recognised, purely in
order to be removed, and the uploader says so rather than dropping it
silently.

Deliberately strict: a bare number is far more likely to be part of a name
("Set of 3") than a price, so a currency marker is required.
"""

import re

PRICE = re.compile(
    r"(?:\u20b9|Rs\.?|INR)\s*(\d[\d,]*)"      # ₹250, Rs 250, Rs.250, INR 250
    r"|(\d[\d,]*)\s*(?:/-|rupees?|rs\b)",      # 250/-, 250 rupees, 250 rs
    re.IGNORECASE,
)


def find_price(text: str) -> tuple[str | None, str]:
    """-> (price as '\u20b9250' or None, the text with the price removed)."""
    match = PRICE.search(text)
    if not match:
        return None, text
    amount = (match.group(1) or match.group(2)).replace(",", "")
    if not amount.isdigit() or int(amount) <= 0:
        return None, text
    cleaned = re.sub(r"[ \t]{2,}", " ", text[: match.start()] + " " + text[match.end():]).strip()
    return f"\u20b9{int(amount):,}", cleaned
