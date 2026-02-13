import logging
import os
import sys

from app.core.config import get_settings

settings = get_settings()


def _build_formatter() -> logging.Formatter:
    if settings.log_format.lower() == "json":
        try:
            from pythonjsonlogger import jsonlogger  # pylint: disable=import-outside-toplevel

            return jsonlogger.JsonFormatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d"
            )
        except Exception:
            # Fallback to text logs if JSON formatter dependency is unavailable.
            pass
    return logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def _configure_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    formatter = _build_formatter()

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    if settings.log_file:
        log_dir = os.path.dirname(settings.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(settings.log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


_configure_logging()
logger = logging.getLogger(__name__)
