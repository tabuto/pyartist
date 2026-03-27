"""
sync_engine.py — Image processing (Pillow) + gallery.json generation + FTP sync.
Implementazione dettagliata nei task TSK-10, TSK-11, TSK-12.
"""

import json
import ftplib
import os
from pathlib import Path

from PIL import Image


GALLERY_JSON_PATH = Path(__file__).parent.parent / "website" / "data" / "gallery.json"
MAX_IMAGE_SIZE = 1920
MAX_THUMB_SIZE = 400
JPEG_QUALITY = 85


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


def ftp_sync(files: list[tuple[Path, str]]) -> list[dict]:
    """
    Carica una lista di file sul server FTP.
    files: lista di (percorso_locale, percorso_remoto)
    Ritorna un log con esito per ogni file.
    """
    host = os.environ["FTP_HOST"]
    user = os.environ["FTP_USER"]
    password = os.environ["FTP_PASS"]
    base_path = os.environ.get("FTP_PATH", "/")

    log = []
    with ftplib.FTP(host) as ftp:
        ftp.login(user, password)
        for local_path, remote_name in files:
            remote_path = f"{base_path}/{remote_name}"
            try:
                with open(local_path, "rb") as f:
                    ftp.storbinary(f"STOR {remote_path}", f)
                log.append({"file": remote_name, "status": "ok"})
            except Exception as exc:
                log.append({"file": remote_name, "status": "error", "error": str(exc)})
    return log
