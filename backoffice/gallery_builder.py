"""
gallery_builder.py — Build gallery JSON and downloadable ZIP archives.
"""

import io
import json
import logging
import zipfile
from pathlib import Path

from models import Gallery

GALLERY_JSON_PATH = Path(__file__).parent.parent / "website" / "data" / "gallery.json"

logger = logging.getLogger(__name__)


def generate_gallery_json(gallery: Gallery) -> dict:
    """Build structured gallery JSON, write to website/data/gallery.json, return dict."""
    categories: dict[str, list] = {}

    for item in gallery.items:
        artwork = item.artwork
        cat_name = artwork.category
        categories.setdefault(cat_name, [])
        categories[cat_name].append(artwork.to_dict())

    data = {
        "gallery_name": gallery.name,
        "categories": [
            {"name": cat, "slug": _slugify(cat), "items": items}
            for cat, items in categories.items()
        ],
    }

    GALLERY_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(GALLERY_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


def build_zip(gallery: Gallery) -> io.BytesIO:
    """Build a ZIP archive with gallery.json + artwork images from Drive."""
    from drive import DriveClient

    client = DriveClient()
    gallery_data = generate_gallery_json(gallery)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("data/gallery.json", json.dumps(gallery_data, ensure_ascii=False, indent=2))

        for item in gallery.items:
            artwork = item.artwork
            slug = _slugify(artwork.category)
            title_slug = _slugify(artwork.title)
            filename = f"{title_slug}-{artwork.id}"

            if artwork.drive_file_id:
                try:
                    img_bytes = client.download_file(artwork.drive_file_id)
                    zf.writestr(f"img/art/{slug}/{filename}.jpg", img_bytes.read())
                except Exception as exc:
                    logger.warning(
                        "Impossibile scaricare immagine Drive %s per opera %s: %s",
                        artwork.drive_file_id,
                        artwork.id,
                        exc,
                    )

            if artwork.drive_thumb_id:
                try:
                    thumb_bytes = client.download_file(artwork.drive_thumb_id)
                    zf.writestr(f"img/art/{slug}/thumb_{filename}.jpg", thumb_bytes.read())
                except Exception as exc:
                    logger.warning(
                        "Impossibile scaricare thumbnail Drive %s per opera %s: %s",
                        artwork.drive_thumb_id,
                        artwork.id,
                        exc,
                    )

    buf.seek(0)
    return buf


def _slugify(text: str) -> str:
    import re

    text = text.lower().strip()
    text = re.sub(r"[àáâãäå]", "a", text)
    text = re.sub(r"[èéêë]", "e", text)
    text = re.sub(r"[ìíîï]", "i", text)
    text = re.sub(r"[òóôõö]", "o", text)
    text = re.sub(r"[ùúûü]", "u", text)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")
