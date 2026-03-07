from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List, Optional

# Always resolve .env relative to this file's location (backend/)
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "KameArt Consent Form API"
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Google Drive — OAuth2 credentials (personal Google account)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REFRESH_TOKEN: str = ""
    GOOGLE_DRIVE_FOLDER_ID: str = ""

    model_config = {"env_file": str(_ENV_FILE)}


settings = Settings()
