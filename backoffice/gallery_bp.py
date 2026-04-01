"""
gallery_bp.py — Blueprint for Gallery management.
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
from utils import login_required

gallery_bp = Blueprint("gallery", __name__, url_prefix="/gallery")


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
        json_filename = request.form.get("json_filename", "").strip() or "gallery.json"
        if not json_filename.endswith(".json"):
            json_filename += ".json"
        if not name:
            flash("Il nome della galleria è obbligatorio.", "error")
            return render_template("gallery/new_gallery.html")
        gallery_id = tdb.gallery_create(name, description or None, json_filename)
        flash(f"Galleria «{name}» creata.", "success")
        return redirect(url_for("gallery.gallery_detail", id=gallery_id))
    return render_template("gallery/new_gallery.html")


@gallery_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_gallery(id):
    gallery = tdb.gallery_get(id)
    if request.method == "POST":
        name = request.form.get("name", gallery.name).strip()
        description = request.form.get("description", "").strip()
        json_filename = request.form.get("json_filename", "").strip() or gallery.json_filename
        if not json_filename.endswith(".json"):
            json_filename += ".json"
        tdb.gallery_update(id, name, description or None, json_filename)
        flash(f"Galleria «{name}» aggiornata.", "success")
        return redirect(url_for("gallery.gallery_detail", id=id))
    return render_template("gallery/edit_gallery.html", gallery=gallery)


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
