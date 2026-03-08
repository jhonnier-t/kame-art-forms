from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.models.consent import ConsentFormRequest, ConsentFormResponse
from app.services.consent_service import consent_service

log = get_logger("routes.consent")
router = APIRouter()


@router.get(
    "",
    summary="Estado del servicio de consentimiento",
    include_in_schema=False,
)
async def consent_status():
    return JSONResponse({
        "service": "KameArt Consent API",
        "status": "online",
        "endpoints": {
            "submit": "POST /api/consent/submit",
        },
    })


@router.post(
    "/submit",
    response_model=ConsentFormResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an informed consent form",
)
async def submit_consent(form: ConsentFormRequest) -> ConsentFormResponse:
    log.info("New consent submission — name=%s doc=%s", form.personal_data.full_name, form.personal_data.document_id)
    try:
        result = consent_service.submit(form)
        log.info("Consent stored — reference=%s", result.reference_number)
        return result
    except Exception as exc:
        log.error("Consent submission failed — %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el formulario: {exc}",
        ) from exc
