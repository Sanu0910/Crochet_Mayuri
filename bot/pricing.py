"""Reading a price out of a Telegram caption.

Deliberately strict: a bare number is far more likely to be part of a name
("Set of 3") than a price, so a currency marker is required. Anything the
shop actually charges will have one.
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
