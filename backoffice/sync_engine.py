"""
sync_engine.py — Image processing (Pillow) + gallery.json generation + FTP sync.
Implementazione dettagliata nei task TSK-10, TSK-11, TSK-12.
"""

import ftplib
import io
import json
import logging
import os
from pathlib import Path

from PIL import Image

GALLERY_JSON_PATH = Path(__file__).parent.parent / "website" / "data" / "gallery.json"
MAX_IMAGE_SIZE = 1920
MAX_THUMB_SIZE = 400
JPEG_QUALITY = 85

logger = logging.getLogger(__name__)


def optimize_image(src_path: Path, dest_path: Path) -> Path:
    """Ridimensiona a max 1920px (lato lungo) e salva in JPEG qualità 85."""
    with Image.open(src_path) as img:
        img.thumbnail((MAX_IMAGE_SIZE, MAX_IMAGE_SIZE), Image.LANCZOS)
        img.save(dest_path, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return dest_path


def generate_thumbnail(src_path: Path, dest_path: Path) -> Path:
    """Genera una thumbnail a max 400px."""
    with Image.open(src_path) as img:
        img.thumbnail((MAX_THUMB_SIZE, MAX_THUMB_SIZE), Image.LANCZOS)
        img.save(dest_path, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return dest_path


def generate_json(artworks) -> None:
    """Esporta le opere pubblicate (ordinate per position) in gallery.json."""
    data = [aw.to_dict() for aw in artworks]
    GALLERY_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(GALLERY_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def ftp_sync(
    gallery_json: bytes | io.BytesIO,
    images: list[tuple[io.BytesIO, str, str]],
    md_files: list[tuple[io.BytesIO, str]] | None = None,
    gallery_json_path: str | None = None,
) -> list[dict]:
    """Carica gallery.json, immagini per categoria e file .md sul server FTP.

    Args:
        gallery_json: contenuto del gallery.json come bytes o BytesIO.
        images: lista di (stream, category_slug, filename) — stream da Google Drive.
        md_files: lista opzionale di (stream, filename) per file Markdown.
        gallery_json_path: percorso remoto del file JSON; se None usa FTP_GALLERY_JSON_PATH.

    Variabili d'ambiente richieste:
        FTP_HOST, FTP_USER, FTP_PASSWORD
    Variabili d'ambiente opzionali:
        FTP_PORT (default 21)
        FTP_USE_TLS (default false; impostare "true" per FTPS esplicito)
        FTP_IMAGES_PATH (default /img/art) — percorso base delle immagini sul server
        FTP_GALLERY_JSON_PATH (default /data/gallery.json) — percorso gallery.json sul server
        FTP_CONTENT_PATH (default /content) — percorso file .md sul server

    Returns:
        Lista di dict {"file": str, "status": "ok"|"error", "error": str (opzionale)}.
    """
    host = os.environ["FTP_HOST"]
    port = int(os.environ.get("FTP_PORT", 21))
    user = os.environ["FTP_USER"]
    password = os.environ.get("FTP_PASSWORD") or os.environ.get("FTP_PASS", "")
    use_tls = os.environ.get("FTP_USE_TLS", "false").lower() == "true"
    images_path = os.environ.get("FTP_IMAGES_PATH", "/img/art").rstrip("/")
    resolved_gallery_json_path = gallery_json_path or os.environ.get("FTP_GALLERY_JSON_PATH", "/data/gallery.json")
    content_path = os.environ.get("FTP_CONTENT_PATH", "/content").rstrip("/")

    log: list[dict] = []

    ftp_cls = ftplib.FTP_TLS if use_tls else ftplib.FTP
    ftp = ftp_cls()
    try:
        ftp.connect(host, port)
        ftp.login(user, password)
        if use_tls:
            ftp.prot_p()  # Protegge il canale dati con TLS

        # ── Carica gallery.json ────────────────────────────────────────────
        _ftp_upload_stream(
            ftp,
            gallery_json if isinstance(gallery_json, io.BytesIO) else io.BytesIO(gallery_json),
            resolved_gallery_json_path,
            log,
        )

        # ── Carica immagini per categoria ──────────────────────────────────
        for stream, category_slug, filename in images:
            _ftp_ensure_dirs(ftp, f"{images_path}/{category_slug}")
            remote_path = f"{images_path}/{category_slug}/{filename}"
            stream.seek(0)
            _ftp_upload_stream(ftp, stream, remote_path, log)

        # ── Carica file .md ────────────────────────────────────────────────
        if md_files:
            _ftp_ensure_dirs(ftp, content_path)
            for stream, filename in md_files:
                stream.seek(0)
                remote_path = f"{content_path}/{filename}"
                _ftp_upload_stream(ftp, stream, remote_path, log)

    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()

    return log


# ── Helpers ────────────────────────────────────────────────────────────────────

def _ftp_ensure_dirs(ftp: ftplib.FTP, remote_dir: str) -> None:
    """Crea ricorsivamente le directory remote se non esistono."""
    parts = [p for p in remote_dir.split("/") if p]
    current = ""
    for part in parts:
        current = f"{current}/{part}"
        try:
            ftp.mkd(current)
        except ftplib.error_perm as e:
            # 550 indica che la directory esiste già — ignoriamo
            if not str(e).startswith("550"):
                raise


def _ftp_upload_stream(
    ftp: ftplib.FTP,
    stream: io.BytesIO,
    remote_path: str,
    log: list[dict],
) -> None:
    """Carica uno stream BytesIO sul server FTP e aggiorna il log."""
    try:
        ftp.storbinary(f"STOR {remote_path}", stream)
        logger.info("FTP upload OK: %s", remote_path)
        log.append({"file": remote_path, "status": "ok"})
    except Exception as exc:
        logger.error("FTP upload ERRORE %s: %s", remote_path, exc)
        log.append({"file": remote_path, "status": "error", "error": str(exc)})
