import logging

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.core.config import settings

logger = logging.getLogger(__name__)


class MongoService:
    """Persists consent records to MongoDB Atlas.

    Lazily initialises the client on first use.
    Fails silently — a broken connection must never block the main flow.
    """

    def __init__(self) -> None:
        self._client: MongoClient | None = None

    def _get_collection(self):
        if self._client is None:
            self._client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        return self._client[settings.MONGO_DB_NAME]["consent_records"]

    def save_consent(self, record: dict) -> str | None:
        """Insert a consent record and return the inserted document ID (str).

        Returns None on failure so the caller can proceed without raising.
        """
        if not settings.MONGO_URI or not settings.MONGO_DB_NAME:
            return None
        try:
            collection = self._get_collection()
            result = collection.insert_one(record)
            return str(result.inserted_id)
        except PyMongoError as exc:
            logger.error("MongoDB insert failed: %s", exc)
            return None


mongo_service = MongoService()
