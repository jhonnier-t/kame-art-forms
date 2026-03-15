import base64
import io

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger("services.drive")
_SCOPES = ["https://www.googleapis.com/auth/drive.file"]


class DriveService:
    """Handles all interactions with the Google Drive API.

    Uses OAuth2 refresh token for authentication with a personal Google account.
    The service is lazily instantiated on first use.
    """

    def __init__(self) -> None:
        self._service = None

    def _get_service(self):
        if self._service is None:
            credentials = Credentials(
                token=None,
                refresh_token=settings.GOOGLE_REFRESH_TOKEN,
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=_SCOPES,
            )
            credentials.refresh(Request())
            self._service = build(
                "drive", "v3", credentials=credentials, cache_discovery=False
            )
        return self._service

    def create_folder(self, name: str, parent_id: str) -> str:
        """Return the ID of an existing subfolder with this name, or create it."""
        service = self._get_service()
        query = (
            f"name='{name}' "
            f"and '{parent_id}' in parents "
            f"and mimeType='application/vnd.google-apps.folder' "
            f"and trashed=false"
        )
        existing = service.files().list(q=query, fields="files(id)", pageSize=1).execute()
        files = existing.get("files", [])
        if files:
            log.debug("Drive folder already exists — %s", name)
            return files[0]["id"]
        log.debug("Creating Drive folder — %s", name)
        metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }
        folder = service.files().create(body=metadata, fields="id").execute()
        return folder["id"]

    def _upload_bytes(self, content: bytes, filename: str, mimetype: str, folder_id: str) -> str:
        """Upload raw bytes to the given Drive folder and return the file ID."""
        service = self._get_service()
        buffer = io.BytesIO(content)
        metadata = {
            "name": filename,
            "parents": [folder_id],
        }
        media = MediaIoBaseUpload(buffer, mimetype=mimetype, resumable=False)
        file = (
            service.files()
            .create(body=metadata, media_body=media, fields="id")
            .execute()
        )
        return file["id"]

    def upload_signature_image(self, signature_base64: str, filename: str, folder_id: str) -> str:
        """Decode a base64 PNG and upload it to Drive."""
        raw = signature_base64.split(",")[-1]
        image_bytes = base64.b64decode(raw)
        return self._upload_bytes(image_bytes, filename, "image/png", folder_id)

    def upload_pdf(self, pdf_bytes: bytes, filename: str, folder_id: str) -> str:
        """Upload a PDF file to Drive."""
        return self._upload_bytes(pdf_bytes, filename, "application/pdf", folder_id)


# Module-level singleton — reuses the authenticated Drive service across requests
drive_service = DriveService()
