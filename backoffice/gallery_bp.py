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

from models import Artwork, Category, Gallery, GalleryItem, db
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
        elif Category.query.filter_by(slug=slug).first():
            flash(f"Esiste già una categoria con slug «{slug}».", "error")
        else:
            max_pos = db.session.query(db.func.max(Category.position)).scalar() or 0
            cat = Category(name=name, slug=slug, position=max_pos + 1)
            db.session.add(cat)
            db.session.commit()
            flash(f"Categoria «{name}» creata.", "success")
        return redirect(url_for("gallery.categories"))

    cats = Category.query.order_by(Category.position).all()
    return render_template("gallery/categories.html", categories=cats)


@gallery_bp.route("/categories/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_category(id):
    cat = Category.query.get_or_404(id)
    if request.method == "POST":
        cat.name = request.form.get("name", cat.name).strip()
        cat.slug = request.form.get("slug", "").strip() or slugify(cat.name)
        db.session.commit()
        flash(f"Categoria «{cat.name}» aggiornata.", "success")
        return redirect(url_for("gallery.categories"))
    return render_template("gallery/edit_category.html", category=cat)


@gallery_bp.route("/categories/<int:id>/delete", methods=["POST"])
@login_required
def delete_category(id):
    cat = Category.query.get_or_404(id)
    if Artwork.query.filter_by(category=cat.slug).first():
        flash(f"Impossibile eliminare: esistono opere nella categoria «{cat.name}».", "error")
    else:
        db.session.delete(cat)
        db.session.commit()
        flash(f"Categoria «{cat.name}» eliminata.", "success")
    return redirect(url_for("gallery.categories"))


# ── Galleries ─────────────────────────────────────────────────────────────────

@gallery_bp.route("/")
@login_required
def gallery_list():
    galleries = Gallery.query.order_by(Gallery.created_at.desc()).all()
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
        gallery = Gallery(name=name, description=description or None)
        db.session.add(gallery)
        db.session.commit()
        flash(f"Galleria «{name}» creata.", "success")
        return redirect(url_for("gallery.gallery_detail", id=gallery.id))
    return render_template("gallery/new_gallery.html")


@gallery_bp.route("/<int:id>")
@login_required
def gallery_detail(id):
    gallery = Gallery.query.get_or_404(id)
    item_artwork_ids = {item.artwork_id for item in gallery.items}
    available = Artwork.query.filter(
        Artwork.id.notin_(item_artwork_ids)
    ).order_by(Artwork.position).all()
    return render_template(
        "gallery/gallery_detail.html",
        gallery=gallery,
        available=available,
    )


@gallery_bp.route("/<int:id>/items/add", methods=["POST"])
@login_required
def add_item(id):
    gallery = Gallery.query.get_or_404(id)
    artwork_id = request.form.get("artwork_id", type=int)
    if artwork_id and not GalleryItem.query.filter_by(
        gallery_id=id, artwork_id=artwork_id
    ).first():
        max_pos = (
            db.session.query(db.func.max(GalleryItem.position))
            .filter_by(gallery_id=id)
            .scalar()
            or 0
        )
        item = GalleryItem(gallery_id=id, artwork_id=artwork_id, position=max_pos + 1)
        db.session.add(item)
        db.session.commit()
        flash("Opera aggiunta alla galleria.", "success")
    return redirect(url_for("gallery.gallery_detail", id=id))


@gallery_bp.route("/<int:id>/items/remove", methods=["POST"])
@login_required
def remove_item(id):
    item_id = request.form.get("item_id", type=int)
    item = GalleryItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Opera rimossa dalla galleria.", "success")
    return redirect(url_for("gallery.gallery_detail", id=id))


@gallery_bp.route("/<int:id>/items/reorder", methods=["POST"])
@login_required
def reorder_items(id):
    ids = request.json.get("ids", [])
    for position, item_id in enumerate(ids):
        GalleryItem.query.filter_by(id=item_id, gallery_id=id).update({"position": position})
    db.session.commit()
    return jsonify({"ok": True})
