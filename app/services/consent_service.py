import re
import unicodedata
import uuid
from datetime import datetime

from app.core.config import settings
from app.models.consent import ConsentFormRequest, ConsentFormResponse
from app.services.drive_service import drive_service


def _generate_reference() -> str:
    return str(uuid.uuid4())[:8].upper()


def _safe_name(text: str) -> str:
    """Normalize to ASCII, remove special chars, replace spaces with underscores."""
    normalized = unicodedata.normalize("NFD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^\w]", "_", ascii_text).strip("_")


class ConsentService:
    """Orchestrates the processing and storage of a consent form submission."""

    def submit(self, form: ConsentFormRequest) -> ConsentFormResponse:
        reference = _generate_reference()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        patient_name = _safe_name(form.personal_data.full_name)
        document_id = form.personal_data.document_id

        # Folder name: NombreCompleto_Cedula  (e.g. Juan_Garcia_Lopez_12345678)
        folder_name = f"{patient_name}_{document_id}"

        # 1. Create a subfolder for this person inside the root Drive folder
        patient_folder_id = drive_service.create_folder(
            folder_name, settings.GOOGLE_DRIVE_FOLDER_ID
        )

        # 2. Upload digital signature image into the subfolder
        sig_filename = f"{folder_name}_firma_{timestamp}.png"
        signature_file_id = drive_service.upload_signature_image(
            form.signature_image,
            sig_filename,
            patient_folder_id,
        )

        # 3. Build the consent record and upload it as JSON into the subfolder
        consent_record = {
            "reference_number": reference,
            "submitted_at": datetime.now().isoformat(),
            "personal_data": form.personal_data.model_dump(mode="json"),
            "consent_data": form.consent_data.model_dump(mode="json"),
            "signature_drive_file_id": signature_file_id,
        }
        json_filename = f"{folder_name}_consentimiento_{timestamp}.json"
        drive_service.upload_json(
            consent_record,
            json_filename,
            patient_folder_id,
        )

        return ConsentFormResponse(
            success=True,
            message="Consentimiento informado registrado exitosamente.",
            reference_number=reference,
            drive_signature_id=signature_file_id,
        )


consent_service = ConsentService()
