import logging
import sys
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config.settings import settings

# Regex patterns to sanitize sensitive tokens
SECRET_PATTERNS = [
    re.compile(r"(sk-[a-zA-Z0-9_\-]{8,})"),
    re.compile(r"(LIVEKIT_API_SECRET[=:]\s*['\"]?)([^'\"\s]+)"),
    re.compile(r"(Authorization:\s*Bearer\s+)([a-zA-Z0-9_\-\.]+)"),
]


class SanitizedFormatter(logging.Formatter):
    """Custom logging formatter that scrubs API keys and secret tokens from logs."""

    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        sanitized = original
        for pattern in SECRET_PATTERNS:
            sanitized = pattern.sub(r"\1***REDACTED***", sanitized)
        return sanitized


def setup_logger(name: str = "jarvis") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = SanitizedFormatter(log_format, date_format)

    # 1. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. Rotating File Handler (%LOCALAPPDATA%\Jarvis\logs\jarvis.log)
    try:
        log_file = settings.LOGS_PATH / "jarvis.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB per file
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"[Logger Warning] Could not initialize file handler at {settings.LOGS_PATH}: {e}")

    logger.propagate = False
    return logger


logger = setup_logger()
