import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

LOGGER_NAME = "aria2tui"
LOG_FILENAME = "aria2tui-debug.log"


def configure_logging(debug: bool = False, log_path: Optional[Path] = None) -> logging.Logger:
    """Configure logging for aria2tui.

    When ``debug`` is False, a NullHandler is attached so that logging
    calls are safe but produce no output. When ``debug`` is True, a
    RotatingFileHandler is attached that writes to ``aria2tui-debug.log``
    in the current working directory (or to ``log_path`` if provided).
    """
    logger = logging.getLogger(LOGGER_NAME)

    # Always set base level high enough for debug messages.
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers if already configured.
    if logger.handlers:
        return logger

    if not debug:
        # Swallow all logs unless explicitly enabled.
        logger.addHandler(logging.NullHandler())
        return logger

    # Determine log file path: current working directory by default.
    if log_path is None:
        log_path = Path.cwd() / LOG_FILENAME

    try:
        handler = RotatingFileHandler(
            log_path,
            maxBytes=1_000_000,  # 1 MB
            backupCount=3,
        )
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except OSError:
        # If we cannot create the file, fall back to a NullHandler so
        # that logging calls remain safe but silent.
        logger.addHandler(logging.NullHandler())

    return logger


def get_logger() -> logging.Logger:
    """Return the shared aria2tui logger instance.

    The logger is configured via :func:`configure_logging` at
    application startup. Calling this before configuration is safe but
    will be effectively a no-op because of the attached NullHandler.
    """
    return logging.getLogger(LOGGER_NAME)
