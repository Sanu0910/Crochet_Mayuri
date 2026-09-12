"""Turning a photo from Telegram into a file the site can serve."""

import io
import re
import unicodedata
from pathlib import Path

from PIL import Image

MAX_WIDTH = 1100
JPEG_QUALITY = 78


def slugify(name: str) -> str:
    """'Ocean Blue Ruffle Scrunchie' -> 'ocean-blue-ruffle-scrunchie'."""
    ascii_name = (
        unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    )
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")
    return slug or "product"


def unique_slug(slug: str, images_dir: Path) -> str:
    """Never overwrite an existing photo — add -2, -3, ... instead."""
    if not (images_dir / f"{slug}.jpg").exists():
        return slug
    n = 2
    while (images_dir / f"{slug}-{n}.jpg").exists():
        n += 1
    return f"{slug}-{n}"


def save_photo(raw: bytes, images_dir: Path, slug: str) -> str:
    """Write the photo at the same size and quality as the rest of the shop.

    Returns the file name (not the full path).
    """
    image = Image.open(io.BytesIO(raw))
    # Telegram strips EXIF orientation, but a forwarded file might still carry
    # it, and a sideways product photo is worse than no photo at all.
    try:
        from PIL import ImageOps

        image = ImageOps.exif_transpose(image)
    except Exception:
        pass
    image = image.convert("RGB")

    if image.width > MAX_WIDTH:
        height = round(image.height * MAX_WIDTH / image.width)
        image = image.resize((MAX_WIDTH, height), Image.LANCZOS)

    images_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{slug}.jpg"
    image.save(
        images_dir / filename,
        "JPEG",
        quality=JPEG_QUALITY,
        optimize=True,
        progressive=True,
    )
    return filename
