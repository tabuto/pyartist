"""
gallery_bp.py — Blueprint for Category and Gallery management.
"""

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

import turso_db as tdb
from utils import login_required, slugify

gallery_bp = Blueprint("gallery", __name__, url_prefix="/gallery")


# ── Categories ────────────────────────────────────────────────────────────────

@gallery_bp.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        slug = request.form.get("slug", "").strip() or slugify(name)
        if not name:
            flash("Il nome della categoria è obbligatorio.", "error")
        elif tdb.category_by_slug(slug):
            flash(f"Esiste già una categoria con slug «{slug}».", "error")
        else:
            max_pos = tdb.category_max_position()
            tdb.category_create(name, slug, max_pos + 1)
            flash(f"Categoria «{name}» creata.", "success")
        return redirect(url_for("gallery.categories"))

    cats = tdb.category_list()
    return render_template("gallery/categories.html", categories=cats)


@gallery_bp.route("/categories/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_category(id):
    cat = tdb.category_get(id)
    if request.method == "POST":
        new_name = request.form.get("name", cat.name).strip()
        new_slug = request.form.get("slug", "").strip() or slugify(new_name)
        tdb.category_update(id, new_name, new_slug)
        flash(f"Categoria «{new_name}» aggiornata.", "success")
        return redirect(url_for("gallery.categories"))
    return render_template("gallery/edit_category.html", category=cat)


@gallery_bp.route("/categories/<int:id>/delete", methods=["POST"])
@login_required
def delete_category(id):
    cat = tdb.category_get(id)
    if tdb.category_has_artworks(cat.slug):
        flash(f"Impossibile eliminare: esistono opere nella categoria «{cat.name}».", "error")
    else:
        tdb.category_delete(id)
        flash(f"Categoria «{cat.name}» eliminata.", "success")
    return redirect(url_for("gallery.categories"))


# ── Galleries ─────────────────────────────────────────────────────────────────

@gallery_bp.route("/")
@login_required
def gallery_list():
    galleries = tdb.gallery_list()
    return render_template("gallery/gallery_list.html", galleries=galleries)


@gallery_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_gallery():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if not name:
            flash("Il nome della galleria è obbligatorio.", "error")
            return render_template("gallery/new_gallery.html")
        gallery_id = tdb.gallery_create(name, description or None)
        flash(f"Galleria «{name}» creata.", "success")
        return redirect(url_for("gallery.gallery_detail", id=gallery_id))
    return render_template("gallery/new_gallery.html")


@gallery_bp.route("/<int:id>")
@login_required
def gallery_detail(id):
    gallery = tdb.gallery_get(id)
    available = tdb.artwork_not_in_gallery(id)
    return render_template(
        "gallery/gallery_detail.html",
        gallery=gallery,
        available=available,
    )


@gallery_bp.route("/<int:id>/items/add", methods=["POST"])
@login_required
def add_item(id):
    tdb.gallery_get(id)  # verifica esistenza (abort 404 se non esiste)
    artwork_id = request.form.get("artwork_id", type=int)
    if artwork_id and not tdb.gallery_item_exists(id, artwork_id):
        max_pos = tdb.gallery_item_max_position(id)
        tdb.gallery_item_add(id, artwork_id, max_pos + 1)
        flash("Opera aggiunta alla galleria.", "success")
    return redirect(url_for("gallery.gallery_detail", id=id))


@gallery_bp.route("/<int:id>/items/remove", methods=["POST"])
@login_required
def remove_item(id):
    item_id = request.form.get("item_id", type=int)
    tdb.gallery_item_get(item_id)  # abort 404 se non esiste
    tdb.gallery_item_delete(item_id)
    flash("Opera rimossa dalla galleria.", "success")
    return redirect(url_for("gallery.gallery_detail", id=id))


@gallery_bp.route("/<int:id>/items/reorder", methods=["POST"])
@login_required
def reorder_items(id):
    ids = request.json.get("ids", [])
    tdb.gallery_item_reorder([(item_id, position) for position, item_id in enumerate(ids)])
    return jsonify({"ok": True})
