"""
sync_bp.py — Blueprint for sync panel (ZIP export + FTP publish).
"""

import io
import json
import logging

import requests
from flask import Blueprint, flash, redirect, render_template, send_file, url_for

import turso_db as tdb
from utils import login_required

sync_bp = Blueprint("sync_panel", __name__, url_prefix="/sync")

logger = logging.getLogger(__name__)


@sync_bp.route("/")
@login_required
def sync():
    galleries = tdb.gallery_list()
    return render_template("sync/sync.html", galleries=galleries)


@sync_bp.route("/zip/<int:gallery_id>", methods=["POST"])
@login_required
def download_zip(gallery_id):
    gallery = tdb.gallery_get(gallery_id)
    include_images = request.form.get("include_images", "1") == "1"
    try:
        from gallery_builder import build_zip
        buf = build_zip(gallery, include_images=include_images)
    except Exception as exc:
        flash(f"Errore durante la generazione dello ZIP: {exc}", "error")
        return redirect(url_for("sync_panel.sync"))

    return send_file(
        buf,
        mimetype="application/zip",
        as_attachment=True,
        download_name="gallery-export.zip",
    )


@sync_bp.route("/ftp/<int:gallery_id>", methods=["POST"])
@login_required
def ftp_publish(gallery_id):
    gallery = tdb.gallery_get(gallery_id)
    include_images = request.form.get("include_images", "1") == "1"

    try:
        from gallery_builder import generate_gallery_json, _slugify
        from sync_engine import ftp_sync

        # Genera gallery.json e lo converte in bytes
        gallery_data = generate_gallery_json(gallery)
        gallery_json_bytes = json.dumps(gallery_data, ensure_ascii=False, indent=2).encode("utf-8")

        # Percorso FTP: usa json_filename della gallery, con fallback alla variabile d'ambiente
        import os as _os
        json_filename = getattr(gallery, "json_filename", None) or "gallery.json"
        ftp_base = _os.environ.get("FTP_REMOTE_BASE_PATH", "/httpdocs").rstrip("/")
        ftp_gallery_json_path = (
            _os.environ.get("FTP_GALLERY_JSON_PATH")
            if not getattr(gallery, "json_filename", None)
            else f"{ftp_base}/data/{json_filename}"
        )

        # Scarica immagini da Cloudinary come stream HTTP
        images: list[tuple[io.BytesIO, str, str]] = []

        if include_images:
            for item in sorted(gallery.items, key=lambda i: i.position):
                artwork = item.artwork
                cat_slug = _slugify(artwork.category)
                title_slug = _slugify(artwork.title)
                base_name = f"{title_slug}-{artwork.id}"

                if artwork.drive_file_id:
                    try:
                        stream = _download_url(artwork.drive_file_id)
                        images.append((stream, cat_slug, f"{base_name}.jpg"))
                    except Exception as exc:
                        logger.warning(
                            "FTP publish: impossibile scaricare immagine %s per opera %s: %s",
                            artwork.drive_file_id, artwork.id, exc,
                        )
                        flash(
                            f"Attenzione: immagine «{artwork.title}» non scaricata ({exc}).",
                            "warning",
                        )

                if artwork.drive_thumb_id:
                    try:
                        stream = _download_url(artwork.drive_thumb_id)
                        images.append((stream, cat_slug, f"thumb_{base_name}.jpg"))
                    except Exception as exc:
                        logger.warning(
                            "FTP publish: impossibile scaricare thumbnail %s per opera %s: %s",
                            artwork.drive_thumb_id, artwork.id, exc,
                        )
                        flash(
                            f"Attenzione: thumbnail «{artwork.title}» non scaricata ({exc}).",
                            "warning",
                        )

        log = ftp_sync(gallery_json_bytes, images, gallery_json_path=ftp_gallery_json_path)
        errors = [e for e in log if e["status"] != "ok"]
        if errors:
            flash(
                f"FTP completato con {len(errors)} errori: "
                + "; ".join(f"{e['file']}: {e.get('error', '')}" for e in errors),
                "warning",
            )
        else:
            flash(
                f"Pubblicazione FTP completata: {len(log)} file caricati con successo.",
                "success",
            )

    except Exception as exc:
        flash(f"Errore FTP: {exc}", "error")

    return redirect(url_for("sync_panel.sync"))


def _download_url(url: str, timeout: int = 30) -> io.BytesIO:
    """Scarica un file da URL (es. Cloudinary CDN) e lo restituisce come BytesIO."""
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return io.BytesIO(resp.content)
