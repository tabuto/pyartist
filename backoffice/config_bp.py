"""
config_bp.py — Blueprint per la sezione Configurazione:
gestisce Categorie, Formati, Tecniche e Collezioni.
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for

import turso_db as tdb
from utils import login_required, slugify

config_bp = Blueprint("config", __name__, url_prefix="/config")


# ── Pagina principale ─────────────────────────────────────────────────────────

@config_bp.route("/")
@login_required
def index():
    return render_template(
        "config/index.html",
        categories=tdb.category_list(),
        formati=tdb.formato_list(),
        tecniche=tdb.tecnica_list(),
        collezioni=tdb.collezione_list(),
    )


# ── Categorie ─────────────────────────────────────────────────────────────────

@config_bp.route("/categories", methods=["POST"])
@login_required
def category_create():
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
    return redirect(url_for("config.index") + "#categorie")


@config_bp.route("/categories/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_category(id):
    cat = tdb.category_get(id)
    if request.method == "POST":
        new_name = request.form.get("label", cat.name).strip() or cat.name
        new_slug = request.form.get("slug", "").strip() or slugify(new_name)
        tdb.category_update(id, new_name, new_slug)
        flash(f"Categoria «{new_name}» aggiornata.", "success")
        return redirect(url_for("config.index") + "#categorie")
    return render_template("config/edit_option.html", section="Categoria", item=cat,
                           display_value=cat.name,
                           back_url=url_for("config.index") + "#categorie",
                           action_url=url_for("config.edit_category", id=id),
                           show_slug=True)


@config_bp.route("/categories/<int:id>/delete", methods=["POST"])
@login_required
def delete_category(id):
    cat = tdb.category_get(id)
    if tdb.category_has_artworks(cat.slug):
        flash(f"Impossibile eliminare: esistono opere nella categoria «{cat.name}».", "error")
    else:
        tdb.category_delete(id)
        flash(f"Categoria «{cat.name}» eliminata.", "success")
    return redirect(url_for("config.index") + "#categorie")


# ── Formati ───────────────────────────────────────────────────────────────────

@config_bp.route("/formati", methods=["POST"])
@login_required
def formato_create():
    label = request.form.get("label", "").strip()
    if not label:
        flash("Il nome del formato è obbligatorio.", "error")
    else:
        tdb.formato_create(label)
        flash(f"Formato «{label}» aggiunto.", "success")
    return redirect(url_for("config.index") + "#formati")


@config_bp.route("/formati/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_formato(id):
    item = tdb.formato_get(id)
    if request.method == "POST":
        label = request.form.get("label", "").strip()
        if label:
            tdb.formato_update(id, label)
            flash(f"Formato aggiornato.", "success")
        return redirect(url_for("config.index") + "#formati")
    return render_template("config/edit_option.html", section="Formato", item=item,
                           display_value=item.label,
                           back_url=url_for("config.index") + "#formati",
                           action_url=url_for("config.edit_formato", id=id))


@config_bp.route("/formati/<int:id>/delete", methods=["POST"])
@login_required
def delete_formato(id):
    tdb.formato_delete(id)
    flash("Formato eliminato.", "success")
    return redirect(url_for("config.index") + "#formati")


# ── Tecniche ──────────────────────────────────────────────────────────────────

@config_bp.route("/tecniche", methods=["POST"])
@login_required
def tecnica_create():
    label = request.form.get("label", "").strip()
    if not label:
        flash("Il nome della tecnica è obbligatorio.", "error")
    else:
        tdb.tecnica_create(label)
        flash(f"Tecnica «{label}» aggiunta.", "success")
    return redirect(url_for("config.index") + "#tecniche")


@config_bp.route("/tecniche/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_tecnica(id):
    item = tdb.tecnica_get(id)
    if request.method == "POST":
        label = request.form.get("label", "").strip()
        if label:
            tdb.tecnica_update(id, label)
            flash("Tecnica aggiornata.", "success")
        return redirect(url_for("config.index") + "#tecniche")
    return render_template("config/edit_option.html", section="Tecnica", item=item,
                           display_value=item.label,
                           back_url=url_for("config.index") + "#tecniche",
                           action_url=url_for("config.edit_tecnica", id=id))


@config_bp.route("/tecniche/<int:id>/delete", methods=["POST"])
@login_required
def delete_tecnica(id):
    tdb.tecnica_delete(id)
    flash("Tecnica eliminata.", "success")
    return redirect(url_for("config.index") + "#tecniche")


# ── Collezioni ────────────────────────────────────────────────────────────────

@config_bp.route("/collezioni", methods=["POST"])
@login_required
def collezione_create():
    label = request.form.get("label", "").strip()
    if not label:
        flash("Il nome della collezione è obbligatorio.", "error")
    else:
        tdb.collezione_create(label)
        flash(f"Collezione «{label}» aggiunta.", "success")
    return redirect(url_for("config.index") + "#collezioni")


@config_bp.route("/collezioni/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_collezione(id):
    item = tdb.collezione_get(id)
    if request.method == "POST":
        label = request.form.get("label", "").strip()
        if label:
            tdb.collezione_update(id, label)
            flash("Collezione aggiornata.", "success")
        return redirect(url_for("config.index") + "#collezioni")
    return render_template("config/edit_option.html", section="Collezione", item=item,
                           display_value=item.label,
                           back_url=url_for("config.index") + "#collezioni",
                           action_url=url_for("config.edit_collezione", id=id))


@config_bp.route("/collezioni/<int:id>/delete", methods=["POST"])
@login_required
def delete_collezione(id):
    tdb.collezione_delete(id)
    flash("Collezione eliminata.", "success")
    return redirect(url_for("config.index") + "#collezioni")
