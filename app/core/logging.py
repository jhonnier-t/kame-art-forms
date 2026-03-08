import logging
import sys

from app.core.config import settings


def _build_logger() -> logging.Logger:
    level = logging.DEBUG if settings.DEBUG else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger("kame_art")
    root.setLevel(level)
    # Avoid duplicate handlers if the module is reloaded (e.g. uvicorn --reload)
    if not root.handlers:
        root.addHandler(handler)

    return root


logger = _build_logger()


def get_logger(name: str) -> logging.Logger:
    """Return a child logger scoped to a service or module.

    Usage:
        from app.core.logging import get_logger
        log = get_logger(__name__)
    """
    return logging.getLogger(f"kame_art.{name}")
