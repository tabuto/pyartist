"""
artworks_bp.py — Blueprint for artwork CRUD + Drive upload.
"""

import logging
import tempfile
from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

from models import Artwork, Category, db
from utils import login_required, slugify

artworks_bp = Blueprint("artworks", __name__, url_prefix="/artworks")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@artworks_bp.route("/")
@login_required
def list_artworks():
    artworks = Artwork.query.order_by(Artwork.position).all()
    return render_template("artworks/list.html", artworks=artworks)


@artworks_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    categories = Category.query.order_by(Category.position).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category_slug = request.form.get("category", "").strip()
        year = request.form.get("year", "").strip()
        technique = request.form.get("technique", "Acquerello su carta").strip()
        file = request.files.get("image")

        if not title or not file or not _allowed(file.filename):
            flash("Titolo e immagine valida sono obbligatori.", "error")
            return render_template("artworks/upload.html", categories=categories)

        # Determine next position
        max_pos = db.session.query(db.func.max(Artwork.position)).scalar() or 0
        artwork = Artwork(
            title=title,
            category=category_slug,
            year=year or None,
            technique=technique,
            position=max_pos + 1,
        )
        db.session.add(artwork)
        db.session.flush()  # get artwork.id

        cat_slug = slugify(category_slug) if category_slug else "uncategorized"
        title_slug = slugify(title)
        filename_base = f"{title_slug}-{artwork.id}"
        artwork.image_path = f"/img/art/{cat_slug}/{filename_base}.jpg"
        artwork.thumb_path = f"/img/art/{cat_slug}/thumb_{filename_base}.jpg"

        # Process image via sync_engine + upload su Cloudinary
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / secure_filename(file.filename)
            file.save(str(tmp_path))

            from sync_engine import generate_thumbnail, optimize_image

            web_path = Path(tmpdir) / f"{filename_base}_web.jpg"
            thumb_path = Path(tmpdir) / f"thumb_{filename_base}.jpg"
            optimize_image(tmp_path, web_path)
            generate_thumbnail(tmp_path, thumb_path)

            # Upload su Cloudinary (opzionale — skip se non configurato)
            try:
                from cloudinary_storage import upload_to_archive

                web_result = upload_to_archive(
                    web_path,
                    folder=f"pyartist/web/{cat_slug}",
                    public_id=filename_base,
                )
                thumb_result = upload_to_archive(
                    thumb_path,
                    folder=f"pyartist/thumbs/{cat_slug}",
                    public_id=f"thumb_{filename_base}",
                )
                # secure_url come riferimento archivio nel DB
                artwork.drive_file_id = web_result["secure_url"]
                artwork.drive_thumb_id = thumb_result["secure_url"]
                # Aggiorna i percorsi pubblici con le URL Cloudinary CDN
                artwork.image_path = web_result["secure_url"]
                artwork.thumb_path = thumb_result["secure_url"]
            except Exception as exc:
                logger.error("Cloudinary upload fallito: %s", exc, exc_info=True)
                flash(f"Cloudinary non disponibile, opera salvata senza sync: {exc}", "warning")

        db.session.commit()
        flash(f"Opera «{title}» caricata con successo.", "success")
        return redirect(url_for("artworks.list_artworks"))

    return render_template("artworks/upload.html", categories=categories)


@artworks_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    artwork = Artwork.query.get_or_404(id)
    categories = Category.query.order_by(Category.position).all()

    if request.method == "POST":
        artwork.title = request.form.get("title", artwork.title).strip()
        artwork.category = request.form.get("category", artwork.category).strip()
        artwork.year = request.form.get("year", "").strip() or None
        artwork.technique = request.form.get("technique", artwork.technique).strip()
        artwork.is_published = bool(request.form.get("is_published"))

        file = request.files.get("image")
        if file and _allowed(file.filename):
            cat_slug = slugify(artwork.category) if artwork.category else "uncategorized"
            title_slug = slugify(artwork.title)
            filename_base = f"{title_slug}-{artwork.id}"
            artwork.image_path = f"/img/art/{cat_slug}/{filename_base}.jpg"
            artwork.thumb_path = f"/img/art/{cat_slug}/thumb_{filename_base}.jpg"

            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir) / secure_filename(file.filename)
                file.save(str(tmp_path))

                from sync_engine import generate_thumbnail, optimize_image

                web_path = Path(tmpdir) / f"{filename_base}_web.jpg"
                thumb_path = Path(tmpdir) / f"thumb_{filename_base}.jpg"
                optimize_image(tmp_path, web_path)
                generate_thumbnail(tmp_path, thumb_path)

                try:
                    from cloudinary_storage import upload_to_archive

                    web_result = upload_to_archive(
                        web_path,
                        folder=f"pyartist/web/{cat_slug}",
                        public_id=filename_base,
                    )
                    thumb_result = upload_to_archive(
                        thumb_path,
                        folder=f"pyartist/thumbs/{cat_slug}",
                        public_id=f"thumb_{filename_base}",
                    )
                    artwork.drive_file_id = web_result["secure_url"]
                    artwork.drive_thumb_id = thumb_result["secure_url"]
                    artwork.image_path = web_result["secure_url"]
                    artwork.thumb_path = thumb_result["secure_url"]
                except Exception as exc:
                    logger.error("Cloudinary upload fallito (edit): %s", exc, exc_info=True)
                    flash(f"Cloudinary non disponibile: {exc}", "warning")

        db.session.commit()
        flash(f"Opera «{artwork.title}» aggiornata.", "success")
        return redirect(url_for("artworks.list_artworks"))

    return render_template("artworks/edit.html", artwork=artwork, categories=categories)


@artworks_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    artwork = Artwork.query.get_or_404(id)

    # Elimina da Cloudinary se presenti URL in archivio
    if artwork.drive_file_id or artwork.drive_thumb_id:
        try:
            from cloudinary_storage import delete_from_archive
            import re

            def _public_id_from_url(url: str) -> str:
                # Estrae il public_id dall'URL Cloudinary
                # es: https://res.cloudinary.com/cloud/image/upload/v123/pyartist/web/cat/name.jpg
                # → pyartist/web/cat/name
                match = re.search(r"/upload/(?:v\d+/)?(.+?)(?:\.\w+)?$", url or "")
                return match.group(1) if match else url

            if artwork.drive_file_id:
                delete_from_archive(_public_id_from_url(artwork.drive_file_id))
            if artwork.drive_thumb_id:
                delete_from_archive(_public_id_from_url(artwork.drive_thumb_id))
        except Exception as exc:
            logger.error("Cloudinary delete fallito: %s", exc, exc_info=True)
            flash(f"Impossibile eliminare file su Cloudinary: {exc}", "warning")

    db.session.delete(artwork)
    db.session.commit()
    flash(f"Opera «{artwork.title}» eliminata.", "success")
    return redirect(url_for("artworks.list_artworks"))


@artworks_bp.route("/reorder", methods=["POST"])
@login_required
def reorder():
    ids = request.json.get("ids", [])
    for position, artwork_id in enumerate(ids):
        Artwork.query.filter_by(id=artwork_id).update({"position": position})
    db.session.commit()
    return jsonify({"ok": True})
