"""
cloudinary_storage.py — Integrazione Cloudinary per storage e CDN immagini.

Configurazione tramite variabile d'ambiente CLOUDINARY_URL (formato:
cloudinary://api_key:api_secret@cloud_name).

Funzioni esposte:
  upload_to_archive(file_path, folder, public_id)  → dict con secure_url, public_id
  delete_from_archive(public_id)                   → dict con result
"""

import os
import cloudinary
import cloudinary.uploader


def _configure() -> None:
    """Configura Cloudinary dalla variabile d'ambiente CLOUDINARY_URL."""
    url = os.environ.get("CLOUDINARY_URL", "")
    if not url:
        raise RuntimeError(
            "Configurazione mancante: CLOUDINARY_URL non impostato nel .env.\n"
            "Formato atteso: cloudinary://api_key:api_secret@cloud_name"
        )
    cloudinary.config(cloudinary_url=url)


def upload_to_archive(
    file_path,
    folder: str = "pyartist",
    public_id: str | None = None,
) -> dict:
    """Carica un file su Cloudinary e restituisce il risultato dell'upload.

    Args:
        file_path: Path locale del file da caricare (str o Path).
        folder:    Cartella di destinazione su Cloudinary (es. "pyartist/web/paesaggi").
        public_id: ID pubblico del file su Cloudinary (opzionale; se None viene
                   generato automaticamente).

    Returns:
        Dizionario Cloudinary con almeno: secure_url, public_id, width, height, format.

    Raises:
        RuntimeError: se CLOUDINARY_URL non è configurato o l'upload fallisce.
    """
    _configure()
    try:
        result = cloudinary.uploader.upload(
            str(file_path),
            folder=folder,
            public_id=public_id,
            resource_type="image",
            overwrite=True,
            invalidate=True,
        )
    except Exception as exc:
        raise RuntimeError(
            f"Cloudinary: errore durante l'upload di '{file_path}': {exc}"
        ) from exc
    return result


def delete_from_archive(public_id: str) -> dict:
    """Elimina un file da Cloudinary tramite public_id.

    Args:
        public_id: ID pubblico del file su Cloudinary.

    Returns:
        Dizionario con il risultato dell'eliminazione ({"result": "ok"} se riuscito).

    Raises:
        RuntimeError: se CLOUDINARY_URL non è configurato o la cancellazione fallisce.
    """
    _configure()
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type="image")
    except Exception as exc:
        raise RuntimeError(
            f"Cloudinary: errore durante la cancellazione di '{public_id}': {exc}"
        ) from exc
    return result
