from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.routes import consent
from app.core.config import settings
from app.core.logging import get_logger

log = get_logger("main")

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    # Disable interactive docs in production
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(consent.router, prefix="/api/consent", tags=["consent"])

log.info("KameArt API starting — debug=%s", settings.DEBUG)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/api/consent")


@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME}
