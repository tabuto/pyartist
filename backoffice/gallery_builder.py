"""
gallery_builder.py — Build gallery JSON and downloadable ZIP archives.
"""

import io
import json
import logging
import zipfile
from pathlib import Path

import turso_db as tdb

GALLERY_JSON_PATH = Path(__file__).parent.parent / "website" / "data" / "gallery.json"

logger = logging.getLogger(__name__)


def generate_gallery_json(gallery) -> dict:
    """Build structured gallery JSON, write to website/data/gallery.json, return dict.

    Le categorie sono ordinate per Category.position (poi alphabeticamente come fallback).
    All'interno di ogni categoria le opere rispettano l'ordinamento GalleryItem.position.
    """
    # Mappa slug → position (per ordinare le categorie nella struttura finale)
    cat_positions: dict[str, int] = {
        c.slug: c.position
        for c in tdb.category_list()
    }

    categories: dict[str, list] = {}
    for item in sorted(gallery.items, key=lambda i: i.position):
        artwork = item.artwork
        cat_slug = _slugify(artwork.category)
        categories.setdefault(cat_slug, [])
        categories[cat_slug].append(artwork.to_dict())

    def _cat_sort_key(cat_slug: str) -> tuple[int, str]:
        return (cat_positions.get(cat_slug, 9999), cat_slug)

    data = {
        "gallery_name": gallery.name,
        "categories": [
            {"name": _cat_display_name(cat_slug, gallery), "slug": cat_slug, "items": items}
            for cat_slug, items in sorted(categories.items(), key=lambda kv: _cat_sort_key(kv[0]))
        ],
    }

    GALLERY_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(GALLERY_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


def build_zip(gallery: Gallery) -> io.BytesIO:
    """Build a ZIP archive with gallery.json + artwork images from Cloudinary.

    Struttura ZIP:
        data/gallery.json
        img/art/{categoria}/{titolo-id}.jpg
        img/art/{categoria}/thumb_{titolo-id}.jpg
    """
    import requests

    gallery_data = generate_gallery_json(gallery)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("data/gallery.json", json.dumps(gallery_data, ensure_ascii=False, indent=2))

        for item in sorted(gallery.items, key=lambda i: i.position):
            artwork = item.artwork
            slug = _slugify(artwork.category)
            title_slug = _slugify(artwork.title)
            filename = f"{title_slug}-{artwork.id}"

            if artwork.drive_file_id:
                try:
                    resp = requests.get(artwork.drive_file_id, timeout=30)
                    resp.raise_for_status()
                    zf.writestr(f"img/art/{slug}/{filename}.jpg", resp.content)
                except Exception as exc:
                    logger.warning(
                        "Impossibile scaricare immagine %s per opera %s: %s",
                        artwork.drive_file_id,
                        artwork.id,
                        exc,
                    )

            if artwork.drive_thumb_id:
                try:
                    resp = requests.get(artwork.drive_thumb_id, timeout=30)
                    resp.raise_for_status()
                    zf.writestr(f"img/art/{slug}/thumb_{filename}.jpg", resp.content)
                except Exception as exc:
                    logger.warning(
                        "Impossibile scaricare thumbnail %s per opera %s: %s",
                        artwork.drive_thumb_id,
                        artwork.id,
                        exc,
                    )

    buf.seek(0)
    return buf


def _cat_display_name(slug: str, gallery: Gallery) -> str:
    """Restituisce il nome visualizzato della categoria dallo slug, cercando tra le opere."""
    for item in gallery.items:
        if _slugify(item.artwork.category) == slug:
            return item.artwork.category
    return slug


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
