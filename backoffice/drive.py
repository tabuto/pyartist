"""
drive.py — Google Drive client for PyArtist backoffice.
Handles folder creation, file upload/download/delete via Service Account credentials.
"""

import os
from io import BytesIO
from pathlib import Path


class DriveClient:
    # Root del progetto (un livello sopra backoffice/)
    _PROJECT_ROOT = Path(__file__).parent.parent

    def __init__(self):
        self._service = None
        sa_env = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "")
        # Se il path è relativo, lo risolve dalla root del progetto
        sa_path = Path(sa_env)
        if sa_env and not sa_path.is_absolute():
            sa_path = self._PROJECT_ROOT / sa_path
        self._sa_file = str(sa_path) if sa_env else ""
        self._root_folder_id = os.environ.get("GOOGLE_DRIVE_ROOT_FOLDER_ID", "")

    def _get_service(self):
        if self._service is not None:
            return self._service
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build

        if not self._sa_file:
            raise RuntimeError(
                "Configurazione mancante: GOOGLE_SERVICE_ACCOUNT_FILE non impostato."
            )
        if not self._root_folder_id:
            raise RuntimeError(
                "Configurazione mancante: GOOGLE_DRIVE_ROOT_FOLDER_ID non impostato."
            )

        creds = Credentials.from_service_account_file(
            self._sa_file,
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        self._service = build("drive", "v3", credentials=creds, cache_discovery=False)
        return self._service

    def get_or_create_folder(self, category: str, subfolder: str) -> str:
        """Ensures pyartist/{subfolder}/{category}/ exists under root, returns folder_id."""
        service = self._get_service()

        def _find_or_create(name: str, parent_id: str) -> str:
            query = (
                f"name='{name}' and '{parent_id}' in parents "
                f"and mimeType='application/vnd.google-apps.folder' and trashed=false"
            )
            try:
                results = (
                    service.files()
                    .list(q=query, fields="files(id, name)", spaces="drive")
                    .execute()
                )
            except Exception as exc:
                self._raise_drive_error("ricerca cartella", name, exc)

            files = results.get("files", [])
            if files:
                return files[0]["id"]

            metadata = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_id],
            }
            try:
                folder = (
                    service.files()
                    .create(body=metadata, fields="id")
                    .execute()
                )
            except Exception as exc:
                self._raise_drive_error("creazione cartella", name, exc)
            return folder["id"]

        pyartist_id = _find_or_create("pyartist", self._root_folder_id)
        sub_id = _find_or_create(subfolder, pyartist_id)
        cat_id = _find_or_create(category, sub_id)
        return cat_id

    def upload_file(
        self,
        src,
        folder_id: str,
        filename: str,
        mime_type: str = "image/jpeg",
    ) -> str:
        """Upload src (Path or BytesIO) to Drive folder, returns drive_file_id."""
        from googleapiclient.http import MediaIoBaseUpload

        service = self._get_service()

        if isinstance(src, Path):
            file_obj = open(src, "rb")
            close_after = True
        else:
            file_obj = src
            close_after = False

        try:
            media = MediaIoBaseUpload(file_obj, mimetype=mime_type, resumable=False)
            metadata = {"name": filename, "parents": [folder_id]}
            try:
                result = (
                    service.files()
                    .create(body=metadata, media_body=media, fields="id")
                    .execute()
                )
            except Exception as exc:
                self._raise_drive_error("upload", filename, exc)
        finally:
            if close_after:
                file_obj.close()

        return result["id"]

    def download_file(self, drive_file_id: str) -> BytesIO:
        """Download file from Drive, returns BytesIO."""
        from googleapiclient.http import MediaIoBaseDownload

        service = self._get_service()
        buf = BytesIO()
        try:
            request = service.files().get_media(fileId=drive_file_id)
            downloader = MediaIoBaseDownload(buf, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        except Exception as exc:
            self._raise_drive_error("download", drive_file_id, exc)

        buf.seek(0)
        return buf

    def delete_file(self, drive_file_id: str) -> None:
        """Delete a file from Drive."""
        service = self._get_service()
        try:
            service.files().delete(fileId=drive_file_id).execute()
        except Exception as exc:
            self._raise_drive_error("eliminazione", drive_file_id, exc)

    def _raise_drive_error(self, operation: str, resource: str, exc: Exception) -> None:
        status = getattr(exc, "status_code", None) or getattr(
            getattr(exc, "resp", None), "status", None
        )
        try:
            status = int(status)
        except (TypeError, ValueError):
            status = 0

        if status in (401, 403):
            raise PermissionError(
                f"Accesso negato a Google Drive durante '{operation}' su '{resource}'. "
                f"Verifica le credenziali del Service Account (errore {status})."
            ) from exc
        raise RuntimeError(
            f"Errore Google Drive durante '{operation}' su '{resource}': {exc}"
        ) from exc
