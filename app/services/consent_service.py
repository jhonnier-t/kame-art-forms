import re
import unicodedata
import uuid
from datetime import datetime

from app.core.config import settings
from app.models.consent import ConsentFormRequest, ConsentFormResponse
from app.services.drive_service import drive_service
from app.services.pdf_service import pdf_service
from app.services.email_service import email_service
from app.services.mongo_service import mongo_service


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
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        submitted_at = now.isoformat()

        patient_name = _safe_name(form.personal_data.full_name)
        document_id = form.personal_data.document_id
        folder_name = f"{patient_name}_{document_id}"

        # 1. Generate PDF first — if this fails nothing is written to Drive
        pdf_bytes = pdf_service.generate(form, reference, submitted_at)

        # 2. Create a subfolder for this person inside the root Drive folder
        patient_folder_id = drive_service.create_folder(
            folder_name, settings.GOOGLE_DRIVE_FOLDER_ID
        )

        # 3. Upload digital signature image into the subfolder
        sig_filename = f"{folder_name}_firma_{timestamp}.png"
        signature_file_id = drive_service.upload_signature_image(
            form.signature_image,
            sig_filename,
            patient_folder_id,
        )

        # 4. Upload PDF into the subfolder
        pdf_filename = f"{folder_name}_consentimiento_{timestamp}.pdf"
        drive_service.upload_pdf(pdf_bytes, pdf_filename, patient_folder_id)

        # 5. Build the consent record and persist to MongoDB (fails silently)
        consent_record = {
            "reference_number": reference,
            "submitted_at": submitted_at,
            "personal_data": form.personal_data.model_dump(mode="json"),
            "consent_data": form.consent_data.model_dump(mode="json"),
            "signature_drive_file_id": signature_file_id,
        }
        mongo_service.save_consent(consent_record)

        # 6. Send email notification to the studio (fails silently)
        email_service.send_consent_notification(
            full_name=form.personal_data.full_name,
            document_id=document_id,
            client_email=form.personal_data.email,
            reference=reference,
            submitted_at=submitted_at,
        )

        return ConsentFormResponse(
            success=True,
            message="Consentimiento informado registrado exitosamente.",
            reference_number=reference,
            drive_signature_id=signature_file_id,
        )


consent_service = ConsentService()
