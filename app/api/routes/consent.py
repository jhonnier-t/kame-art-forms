from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.consent import ConsentFormRequest, ConsentFormResponse
from app.services.consent_service import consent_service

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
    try:
        return consent_service.submit(form)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el formulario: {exc}",
        ) from exc
