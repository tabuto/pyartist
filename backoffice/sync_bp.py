"""
sync_bp.py — Blueprint for sync panel (ZIP export + FTP publish).
"""

from flask import Blueprint, flash, redirect, render_template, send_file, url_for

from models import Gallery
from utils import login_required

sync_bp = Blueprint("sync_panel", __name__, url_prefix="/sync")


@sync_bp.route("/")
@login_required
def sync():
    galleries = Gallery.query.order_by(Gallery.created_at.desc()).all()
    return render_template("sync/sync.html", galleries=galleries)


@sync_bp.route("/zip/<int:gallery_id>", methods=["POST"])
@login_required
def download_zip(gallery_id):
    gallery = Gallery.query.get_or_404(gallery_id)
    from gallery_builder import build_zip

    buf = build_zip(gallery)
    return send_file(
        buf,
        mimetype="application/zip",
        as_attachment=True,
        download_name="gallery-export.zip",
    )


@sync_bp.route("/ftp/<int:gallery_id>", methods=["POST"])
@login_required
def ftp_publish(gallery_id):
    gallery = Gallery.query.get_or_404(gallery_id)
    from gallery_builder import generate_gallery_json
    from sync_engine import GALLERY_JSON_PATH, ftp_sync

    try:
        generate_gallery_json(gallery)
        log = ftp_sync([(GALLERY_JSON_PATH, "data/gallery.json")])
        errors = [e for e in log if e["status"] != "ok"]
        if errors:
            flash(f"FTP completato con {len(errors)} errori: {errors}", "warning")
        else:
            flash("gallery.json pubblicato via FTP con successo.", "success")
    except Exception as exc:
        flash(f"Errore FTP: {exc}", "error")

    return redirect(url_for("sync_panel.sync"))
