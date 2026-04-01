"""
artworks_bp.py — Blueprint for artwork CRUD + Drive upload.
"""

import logging
import tempfile
from pathlib import Path

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

import turso_db as tdb
from utils import login_required, slugify

logger = logging.getLogger(__name__)

artworks_bp = Blueprint("artworks", __name__, url_prefix="/artworks")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@artworks_bp.route("/")
@login_required
def list_artworks():
    artworks = tdb.artwork_list()
    return render_template("artworks/list.html", artworks=artworks)


@artworks_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    categories = tdb.category_list()
    formati = tdb.formato_list()
    tecniche = tdb.tecnica_list()
    collezioni = tdb.collezione_list()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category_slug = request.form.get("category", "").strip()
        year = request.form.get("year", "").strip()
        technique = request.form.get("technique", "").strip()
        formato = request.form.get("formato", "").strip() or None
        tecnica = request.form.get("tecnica", "").strip() or None
        descrizione = request.form.get("descrizione", "").strip() or None
        collezione = request.form.get("collezione", "").strip() or None
        file = request.files.get("image")

        if not title or not file or not _allowed(file.filename):
            flash("Titolo e immagine valida sono obbligatori.", "error")
            return render_template("artworks/upload.html", categories=categories,
                                   formati=formati, tecniche=tecniche, collezioni=collezioni)

        cat_slug = slugify(category_slug) if category_slug else "uncategorized"
        title_slug = slugify(title)

        # Crea il record senza paths per ottenere l'ID
        max_pos = tdb.artwork_max_position()
        artwork_id = tdb.artwork_create(
            title=title,
            category=category_slug,
            year=year or None,
            technique=technique or None,
            image_path=None,
            thumb_path=None,
            drive_file_id=None,
            drive_thumb_id=None,
            is_published=False,
            position=max_pos + 1,
            formato=formato,
            tecnica=tecnica,
            descrizione=descrizione,
            collezione=collezione,
        )

        filename_base = f"{title_slug}-{artwork_id}"
        local_image = f"/img/art/{cat_slug}/{filename_base}.jpg"
        local_thumb = f"/img/art/{cat_slug}/thumb_{filename_base}.jpg"

        # Process image via sync_engine + upload su Cloudinary
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
                tdb.artwork_update(
                    artwork_id,
                    image_path=web_result["secure_url"],
                    thumb_path=thumb_result["secure_url"],
                    drive_file_id=web_result["secure_url"],
                    drive_thumb_id=thumb_result["secure_url"],
                )
            except Exception as exc:
                logger.error("Cloudinary upload fallito: %s", exc, exc_info=True)
                tdb.artwork_update(artwork_id, image_path=local_image, thumb_path=local_thumb)
                flash(f"Cloudinary non disponibile, opera salvata senza sync: {exc}", "warning")

        flash(f"Opera «{title}» caricata con successo.", "success")
        return redirect(url_for("artworks.list_artworks"))

    return render_template("artworks/upload.html", categories=categories,
                           formati=formati, tecniche=tecniche, collezioni=collezioni)


@artworks_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    artwork = tdb.artwork_get(id)
    categories = tdb.category_list()
    formati = tdb.formato_list()
    tecniche = tdb.tecnica_list()
    collezioni = tdb.collezione_list()

    if request.method == "POST":
        new_title = request.form.get("title", artwork.title).strip()
        new_category = request.form.get("category", artwork.category).strip()
        new_year = request.form.get("year", "").strip() or None
        new_technique = request.form.get("technique", "").strip() or None
        new_published = bool(request.form.get("is_published"))
        new_formato = request.form.get("formato", "").strip() or None
        new_tecnica = request.form.get("tecnica", "").strip() or None
        new_descrizione = request.form.get("descrizione", "").strip() or None
        new_collezione = request.form.get("collezione", "").strip() or None

        updates = dict(
            title=new_title,
            category=new_category,
            year=new_year,
            technique=new_technique,
            is_published=new_published,
            formato=new_formato,
            tecnica=new_tecnica,
            descrizione=new_descrizione,
            collezione=new_collezione,
        )

        file = request.files.get("image")
        if file and _allowed(file.filename):
            cat_slug = slugify(new_category) if new_category else "uncategorized"
            title_slug = slugify(new_title)
            filename_base = f"{title_slug}-{artwork.id}"
            local_image = f"/img/art/{cat_slug}/{filename_base}.jpg"
            local_thumb = f"/img/art/{cat_slug}/thumb_{filename_base}.jpg"

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
                    updates.update(
                        image_path=web_result["secure_url"],
                        thumb_path=thumb_result["secure_url"],
                        drive_file_id=web_result["secure_url"],
                        drive_thumb_id=thumb_result["secure_url"],
                    )
                except Exception as exc:
                    logger.error("Cloudinary upload fallito (edit): %s", exc, exc_info=True)
                    updates.update(image_path=local_image, thumb_path=local_thumb)
                    flash(f"Cloudinary non disponibile: {exc}", "warning")

        tdb.artwork_update(id, **updates)
        flash(f"Opera «{new_title}» aggiornata.", "success")
        return redirect(url_for("artworks.list_artworks"))

    return render_template("artworks/edit.html", artwork=artwork, categories=categories,
                           formati=formati, tecniche=tecniche, collezioni=collezioni)


@artworks_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    artwork = tdb.artwork_get(id)

    if artwork.drive_file_id or artwork.drive_thumb_id:
        try:
            import re
            from cloudinary_storage import delete_from_archive

            def _public_id_from_url(url: str) -> str:
                match = re.search(r"/upload/(?:v\d+/)?(.+?)(?:\.\w+)?$", url or "")
                return match.group(1) if match else url

            if artwork.drive_file_id:
                delete_from_archive(_public_id_from_url(artwork.drive_file_id))
            if artwork.drive_thumb_id:
                delete_from_archive(_public_id_from_url(artwork.drive_thumb_id))
        except Exception as exc:
            logger.error("Cloudinary delete fallito: %s", exc, exc_info=True)
            flash(f"Impossibile eliminare file su Cloudinary: {exc}", "warning")

    tdb.artwork_delete(id)
    flash(f"Opera «{artwork.title}» eliminata.", "success")
    return redirect(url_for("artworks.list_artworks"))


@artworks_bp.route("/reorder", methods=["POST"])
@login_required
def reorder():
    ids = request.json.get("ids", [])
    tdb.artwork_reorder([(artwork_id, position) for position, artwork_id in enumerate(ids)])
    return jsonify({"ok": True})
