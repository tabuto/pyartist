"""turso_db.py — accesso a Turso via HTTP REST API.

Bypass di libsql_experimental/WebSocket che blocca i thread Python.
Usare questo modulo al posto delle query SQLAlchemy ORM in tutti i blueprint.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from types import SimpleNamespace

import requests as _http
from flask import abort

logger = logging.getLogger(__name__)

# ── Column lists ───────────────────────────────────────────────────────────────
_AW_COLS = [
    "id", "title", "category", "year", "technique",
    "image_path", "thumb_path", "drive_file_id", "drive_thumb_id",
    "is_published", "position",
    "formato", "tecnica", "descrizione", "collezione",
]
_CAT_COLS = ["id", "name", "slug", "position"]
_GAL_COLS = ["id", "name", "description", "created_at", "updated_at", "json_filename"]
_GI_COLS  = ["id", "gallery_id", "artwork_id", "position"]
_OPT_COLS = ["id", "label", "position"]

# ── Core HTTP helpers ──────────────────────────────────────────────────────────

def _arg(v):
    if v is None:
        return {"type": "null"}
    if isinstance(v, bool):
        return {"type": "integer", "value": "1" if v else "0"}
    if isinstance(v, int):
        return {"type": "integer", "value": str(v)}
    if isinstance(v, float):
        return {"type": "float", "value": str(v)}
    return {"type": "text", "value": str(v)}


def _run(sql: str, params=None, timeout: int = 6) -> dict:
    url = os.environ.get("TURSO_URL", "").replace("libsql://", "https://")
    token = os.environ.get("TURSO_AUTH_TOKEN", "")
    if not url or not token:
        raise RuntimeError("TURSO_URL / TURSO_AUTH_TOKEN non configurati")
    stmt: dict = {"sql": sql}
    if params:
        stmt["args"] = [_arg(p) for p in params]
    resp = _http.post(
        f"{url}/v2/pipeline",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"requests": [{"type": "execute", "stmt": stmt}, {"type": "close"}]},
        timeout=timeout,
    )
    resp.raise_for_status()
    result = resp.json()["results"][0]
    if result.get("type") == "error":
        raise RuntimeError(result["error"]["message"])
    return result["response"]["result"]


def execute(sql: str, params=None, timeout: int = 6) -> list[list]:
    """SELECT: ritorna lista di righe (lista di valori)."""
    result = _run(sql, params, timeout)
    return [[cell.get("value") for cell in row] for row in result.get("rows", [])]


def execute_write(sql: str, params=None, timeout: int = 6) -> int:
    """INSERT/UPDATE/DELETE: ritorna rows_affected."""
    result = _run(sql, params, timeout)
    return result.get("rows_affected", 0)


def last_insert_id(timeout: int = 6) -> int:
    rows = execute("SELECT last_insert_rowid()", timeout=timeout)
    return int(rows[0][0])


# ── Object builders ────────────────────────────────────────────────────────────

def _cast(d: dict) -> dict:
    for k in ("id", "position", "gallery_id", "artwork_id"):
        if k in d and d[k] is not None:
            d[k] = int(d[k])
    if "is_published" in d:
        d["is_published"] = bool(int(d["is_published"])) if d["is_published"] is not None else False
    for k in ("created_at", "updated_at"):
        if k in d and isinstance(d[k], str):
            try:
                d[k] = datetime.fromisoformat(d[k])
            except Exception:
                pass
    return d


class ArtworkNS(SimpleNamespace):
    """SimpleNamespace per Artwork con to_dict() compatibile col modello ORM."""

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "category": self.category,
            "image": self.image_path,
            "thumb": self.thumb_path,
            "details": (
                f"{self.year}, {self.technique}" if self.year else (self.technique or "")
            ),
            "formato": self.formato or "",
            "tecnica": self.tecnica or "",
            "descrizione": self.descrizione or "",
        }


def _make(row: list, cols: list, cls=SimpleNamespace):
    return cls(**_cast(dict(zip(cols, row))))


def _make_artwork(row: list) -> ArtworkNS:
    return _make(row, _AW_COLS, ArtworkNS)


# ── Artwork helpers ────────────────────────────────────────────────────────────

_AW_SELECT = f"SELECT {', '.join(_AW_COLS)} FROM artwork"


def artwork_list() -> list[ArtworkNS]:
    rows = execute(f"{_AW_SELECT} ORDER BY position")
    return [_make_artwork(r) for r in rows]


def artwork_get(id: int) -> ArtworkNS:
    rows = execute(f"{_AW_SELECT} WHERE id = ?", [id])
    if not rows:
        abort(404)
    return _make_artwork(rows[0])


def artwork_max_position() -> int:
    rows = execute("SELECT MAX(position) FROM artwork")
    return int(rows[0][0] or 0)


def artwork_create(
    title, category, year, technique,
    image_path, thumb_path, drive_file_id, drive_thumb_id,
    is_published, position,
    formato=None, tecnica=None, descrizione=None, collezione=None,
) -> int:
    execute_write(
        "INSERT INTO artwork "
        "(title, category, year, technique, image_path, thumb_path, "
        "drive_file_id, drive_thumb_id, is_published, position, "
        "formato, tecnica, descrizione, collezione) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [title, category, year, technique, image_path, thumb_path,
         drive_file_id, drive_thumb_id, is_published, position,
         formato, tecnica, descrizione, collezione],
    )
    return last_insert_id()


def artwork_update(id: int, **fields):
    if not fields:
        return
    sets = ", ".join(f"{k} = ?" for k in fields)
    execute_write(f"UPDATE artwork SET {sets} WHERE id = ?", list(fields.values()) + [id])


def artwork_delete(id: int):
    execute_write("DELETE FROM artwork WHERE id = ?", [id])


def artwork_reorder(id_position_pairs):
    """Aggiorna le posizioni in batch: [(artwork_id, position), ...]"""
    for aw_id, pos in id_position_pairs:
        execute_write("UPDATE artwork SET position = ? WHERE id = ?", [pos, aw_id])


def artwork_not_in_gallery(gallery_id: int) -> list[ArtworkNS]:
    rows = execute(
        f"{_AW_SELECT} "
        "WHERE id NOT IN (SELECT artwork_id FROM gallery_item WHERE gallery_id = ?) "
        "ORDER BY position",
        [gallery_id],
    )
    return [_make_artwork(r) for r in rows]


# ── Category helpers ───────────────────────────────────────────────────────────

_CAT_SELECT = f"SELECT {', '.join(_CAT_COLS)} FROM category"


def category_list() -> list[SimpleNamespace]:
    rows = execute(f"{_CAT_SELECT} ORDER BY position")
    return [_make(r, _CAT_COLS) for r in rows]


def category_get(id: int) -> SimpleNamespace:
    rows = execute(f"{_CAT_SELECT} WHERE id = ?", [id])
    if not rows:
        abort(404)
    return _make(rows[0], _CAT_COLS)


def category_by_slug(slug: str) -> SimpleNamespace | None:
    rows = execute(f"{_CAT_SELECT} WHERE slug = ?", [slug])
    return _make(rows[0], _CAT_COLS) if rows else None


def category_max_position() -> int:
    rows = execute("SELECT MAX(position) FROM category")
    return int(rows[0][0] or 0)


def category_create(name: str, slug: str, position: int) -> int:
    execute_write(
        "INSERT INTO category (name, slug, position) VALUES (?, ?, ?)",
        [name, slug, position],
    )
    return last_insert_id()


def category_update(id: int, name: str, slug: str):
    execute_write("UPDATE category SET name = ?, slug = ? WHERE id = ?", [name, slug, id])


def category_delete(id: int):
    execute_write("DELETE FROM category WHERE id = ?", [id])


def category_has_artworks(slug: str) -> bool:
    rows = execute("SELECT 1 FROM artwork WHERE category = ? LIMIT 1", [slug])
    return bool(rows)


# ── Gallery helpers ────────────────────────────────────────────────────────────

_GAL_SELECT = f"SELECT {', '.join(_GAL_COLS)} FROM gallery"


def _load_gallery_items(gallery_id: int) -> list[SimpleNamespace]:
    """Carica gli item di una gallery con artwork annidato (JOIN)."""
    aw_aliased = [f"a.{c}" for c in _AW_COLS]
    rows = execute(
        f"SELECT gi.id, gi.gallery_id, gi.artwork_id, gi.position, "
        f"{', '.join(aw_aliased)} "
        "FROM gallery_item gi "
        "JOIN artwork a ON gi.artwork_id = a.id "
        "WHERE gi.gallery_id = ? "
        "ORDER BY gi.position",
        [gallery_id],
    )
    n_gi = len(_GI_COLS)
    items = []
    for r in rows:
        item = _make(r[:n_gi], _GI_COLS)
        item.artwork = _make_artwork(r[n_gi:])
        items.append(item)
    return items


def gallery_list() -> list[SimpleNamespace]:
    rows = execute(f"{_GAL_SELECT} ORDER BY created_at DESC")
    galleries = [_make(r, _GAL_COLS) for r in rows]
    for g in galleries:
        g.items = _load_gallery_items(g.id)
    return galleries


def gallery_get(id: int) -> SimpleNamespace:
    rows = execute(f"{_GAL_SELECT} WHERE id = ?", [id])
    if not rows:
        abort(404)
    g = _make(rows[0], _GAL_COLS)
    g.items = _load_gallery_items(g.id)
    return g


def gallery_create(name: str, description: str | None, json_filename: str = "gallery.json") -> int:
    execute_write(
        "INSERT INTO gallery (name, description, json_filename) VALUES (?, ?, ?)",
        [name, description, json_filename],
    )
    return last_insert_id()


def gallery_update(id: int, name: str, description: str | None, json_filename: str):
    execute_write(
        "UPDATE gallery SET name = ?, description = ?, json_filename = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        [name, description, json_filename, id],
    )


def gallery_item_exists(gallery_id: int, artwork_id: int) -> bool:
    rows = execute(
        "SELECT 1 FROM gallery_item WHERE gallery_id = ? AND artwork_id = ? LIMIT 1",
        [gallery_id, artwork_id],
    )
    return bool(rows)


def gallery_item_max_position(gallery_id: int) -> int:
    rows = execute(
        "SELECT MAX(position) FROM gallery_item WHERE gallery_id = ?",
        [gallery_id],
    )
    return int(rows[0][0] or 0)


def gallery_item_add(gallery_id: int, artwork_id: int, position: int) -> int:
    execute_write(
        "INSERT INTO gallery_item (gallery_id, artwork_id, position) VALUES (?, ?, ?)",
        [gallery_id, artwork_id, position],
    )
    return last_insert_id()


def gallery_item_get(id: int) -> SimpleNamespace:
    rows = execute(
        f"SELECT {', '.join(_GI_COLS)} FROM gallery_item WHERE id = ?", [id]
    )
    if not rows:
        abort(404)
    return _make(rows[0], _GI_COLS)


def gallery_item_delete(id: int):
    execute_write("DELETE FROM gallery_item WHERE id = ?", [id])


def gallery_item_reorder(id_position_pairs):
    """Aggiorna le posizioni degli item: [(item_id, position), ...]"""
    for item_id, pos in id_position_pairs:
        execute_write(
            "UPDATE gallery_item SET position = ? WHERE id = ?",
            [pos, item_id],
        )


# ── Option table helpers (Formato / Tecnica / Collezione) ─────────────────────

def _option_list(table: str) -> list[SimpleNamespace]:
    rows = execute(f"SELECT {', '.join(_OPT_COLS)} FROM {table} ORDER BY position, label")
    return [_make(r, _OPT_COLS) for r in rows]


def _option_get(table: str, id: int) -> SimpleNamespace:
    rows = execute(f"SELECT {', '.join(_OPT_COLS)} FROM {table} WHERE id = ?", [id])
    if not rows:
        abort(404)
    return _make(rows[0], _OPT_COLS)


def _option_create(table: str, label: str, position: int) -> int:
    execute_write(f"INSERT INTO {table} (label, position) VALUES (?, ?)", [label, position])
    return last_insert_id()


def _option_max_position(table: str) -> int:
    rows = execute(f"SELECT MAX(position) FROM {table}")
    return int(rows[0][0] or 0)


def _option_update(table: str, id: int, label: str):
    execute_write(f"UPDATE {table} SET label = ? WHERE id = ?", [label, id])


def _option_delete(table: str, id: int):
    execute_write(f"DELETE FROM {table} WHERE id = ?", [id])


def formato_list() -> list[SimpleNamespace]:   return _option_list("formato_option")
def formato_get(id: int):                       return _option_get("formato_option", id)
def formato_create(label: str) -> int:          return _option_create("formato_option", label, _option_max_position("formato_option") + 1)
def formato_update(id: int, label: str):        _option_update("formato_option", id, label)
def formato_delete(id: int):                    _option_delete("formato_option", id)

def tecnica_list() -> list[SimpleNamespace]:    return _option_list("tecnica_option")
def tecnica_get(id: int):                       return _option_get("tecnica_option", id)
def tecnica_create(label: str) -> int:          return _option_create("tecnica_option", label, _option_max_position("tecnica_option") + 1)
def tecnica_update(id: int, label: str):        _option_update("tecnica_option", id, label)
def tecnica_delete(id: int):                    _option_delete("tecnica_option", id)

def collezione_list() -> list[SimpleNamespace]: return _option_list("collezione_option")
def collezione_get(id: int):                    return _option_get("collezione_option", id)
def collezione_create(label: str) -> int:       return _option_create("collezione_option", label, _option_max_position("collezione_option") + 1)
def collezione_update(id: int, label: str):     _option_update("collezione_option", id, label)
def collezione_delete(id: int):                 _option_delete("collezione_option", id)

