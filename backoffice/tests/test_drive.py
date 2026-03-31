"""
tests/test_drive.py — Unit tests for drive.py using unittest.mock.
All Google Drive API calls are mocked; no real credentials required.
The googleapiclient / google-auth packages need not be installed.
"""

import sys
import os
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

# Make backoffice root importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Inject fake google / googleapiclient modules so drive.py imports work ────
_fake_http = MagicMock()
_fake_sa = MagicMock()
_fake_discovery = MagicMock()
_fake_google = MagicMock()
_fake_google_oauth2 = MagicMock()
_fake_google_oauth2_sa = MagicMock()

sys.modules.setdefault("googleapiclient", MagicMock())
sys.modules.setdefault("googleapiclient.discovery", _fake_discovery)
sys.modules.setdefault("googleapiclient.http", _fake_http)
sys.modules.setdefault("google", _fake_google)
sys.modules.setdefault("google.oauth2", _fake_google_oauth2)
sys.modules.setdefault("google.oauth2.service_account", _fake_google_oauth2_sa)

from drive import DriveClient  # noqa: E402  — must come after sys.modules patching


def _make_client(sa_file="fake.json", root="root-folder-id"):
    with patch.dict(os.environ, {
        "GOOGLE_SERVICE_ACCOUNT_FILE": sa_file,
        "GOOGLE_DRIVE_ROOT_FOLDER_ID": root,
    }):
        client = DriveClient()
    return client


def _inject_service(client):
    """Inject a fresh MagicMock service, bypassing lazy init."""
    svc = MagicMock()
    client._service = svc
    return svc


class TestGetOrCreateFolder(unittest.TestCase):
    def _list_resp(self, files):
        r = MagicMock()
        r.execute.return_value = {"files": files}
        return r

    def _create_resp(self, folder_id):
        r = MagicMock()
        r.execute.return_value = {"id": folder_id}
        return r

    def test_folder_exists_returns_existing_id(self):
        """get_or_create_folder returns existing folder id when folder found."""
        client = _make_client()
        svc = _inject_service(client)

        def list_side(**kwargs):
            q = kwargs.get("q", "")
            if "name='pyartist'" in q:
                return self._list_resp([{"id": "pyartist-id", "name": "pyartist"}])
            if "name='web'" in q:
                return self._list_resp([{"id": "web-id", "name": "web"}])
            if "name='paesaggi'" in q:
                return self._list_resp([{"id": "cat-id", "name": "paesaggi"}])
            return self._list_resp([])

        svc.files.return_value.list.side_effect = list_side

        result = client.get_or_create_folder("paesaggi", "web")
        self.assertEqual(result, "cat-id")
        svc.files.return_value.create.assert_not_called()

    def test_folder_created_when_missing(self):
        """get_or_create_folder creates folder when not found."""
        client = _make_client()
        svc = _inject_service(client)

        counter = {"n": 0}

        svc.files.return_value.list.return_value.execute.return_value = {"files": []}

        def create_side(**kwargs):
            counter["n"] += 1
            r = MagicMock()
            r.execute.return_value = {"id": f"new-id-{counter['n']}"}
            return r

        svc.files.return_value.create.side_effect = create_side

        result = client.get_or_create_folder("fiori", "originals")
        self.assertEqual(counter["n"], 3)
        self.assertEqual(result, "new-id-3")


class TestUploadFile(unittest.TestCase):
    def test_upload_path(self):
        """upload_file accepts a Path, calls Drive create, returns id."""
        client = _make_client()
        svc = _inject_service(client)

        svc.files.return_value.create.return_value.execute.return_value = {"id": "drive-file-123"}

        _fake_http.MediaIoBaseUpload.return_value = MagicMock()
        result = client.upload_file(Path(__file__), "folder-id", "test.jpg")

        self.assertEqual(result, "drive-file-123")
        svc.files.return_value.create.assert_called_once()

    def test_upload_bytesio(self):
        """upload_file accepts a BytesIO object."""
        client = _make_client()
        svc = _inject_service(client)

        svc.files.return_value.create.return_value.execute.return_value = {"id": "drive-bytes-456"}

        _fake_http.MediaIoBaseUpload.return_value = MagicMock()
        result = client.upload_file(BytesIO(b"fake image data"), "folder-id", "image.jpg")

        self.assertEqual(result, "drive-bytes-456")


class TestDownloadFile(unittest.TestCase):
    def test_download_returns_bytesio(self):
        """download_file returns a BytesIO with file content."""
        client = _make_client()
        svc = _inject_service(client)

        fake_content = b"image bytes"

        def fake_downloader(buf, request):
            buf.write(fake_content)
            obj = MagicMock()
            obj.next_chunk.return_value = (None, True)
            return obj

        _fake_http.MediaIoBaseDownload.side_effect = fake_downloader

        result = client.download_file("file-id-789")

        self.assertIsInstance(result, BytesIO)
        self.assertEqual(result.read(), fake_content)


class TestDeleteFile(unittest.TestCase):
    def test_delete_calls_api(self):
        """delete_file calls files().delete().execute()."""
        client = _make_client()
        svc = _inject_service(client)

        client.delete_file("file-to-delete")
        svc.files.return_value.delete.assert_called_once_with(fileId="file-to-delete")
        svc.files.return_value.delete.return_value.execute.assert_called_once()


class TestErrorHandling(unittest.TestCase):
    def _http_exc(self, status):
        exc = Exception("HTTP Error")
        resp = MagicMock()
        resp.status = status
        exc.resp = resp
        return exc

    def test_401_raises_permission_error(self):
        """401 from Drive raises PermissionError with Italian message."""
        client = _make_client()
        with self.assertRaises(PermissionError) as ctx:
            client._raise_drive_error("upload", "file.jpg", self._http_exc(401))
        self.assertIn("401", str(ctx.exception))
        self.assertIn("Accesso negato", str(ctx.exception))

    def test_403_raises_permission_error(self):
        """403 from Drive raises PermissionError."""
        client = _make_client()
        with self.assertRaises(PermissionError):
            client._raise_drive_error("download", "file-id", self._http_exc(403))

    def test_503_raises_runtime_error(self):
        """503 (non-auth) from Drive raises RuntimeError."""
        client = _make_client()
        with self.assertRaises(RuntimeError) as ctx:
            client._raise_drive_error("creazione cartella", "pyartist", self._http_exc(503))
        self.assertIn("Errore Google Drive", str(ctx.exception))

    def test_upload_error_propagates(self):
        """upload_file propagates RuntimeError when Drive create fails."""
        client = _make_client()
        svc = _inject_service(client)

        svc.files.return_value.create.return_value.execute.side_effect = Exception("network error")

        _fake_http.MediaIoBaseUpload.return_value = MagicMock()
        with self.assertRaises(RuntimeError):
            client.upload_file(BytesIO(b"data"), "folder", "f.jpg")


if __name__ == "__main__":
    unittest.main()
