"""Structured local logging for the JARVIS runtime.

Logs are written to `%LOCALAPPDATA%\\Jarvis\\logs\\jarvis.log` with rotation.
A sanitising formatter scrubs API keys, bearer tokens and secret assignments so
credentials never reach the log files. File contents, clipboard data and audio
payloads are never logged.
"""

from __future__ import annotations

import logging
import re
import sys
from logging.handlers import RotatingFileHandler

from config.settings import settings

SECRET_PATTERNS = (
    re.compile(r"(sk-[A-Za-z0-9_\-]{6,})"),
    re.compile(r"((?:api[_-]?key|secret|token|password)\s*[=:]\s*)(\S+)", re.IGNORECASE),
    re.compile(r"(Authorization:\s*Bearer\s+)(\S+)"),
    re.compile(r"(eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]+)"),  # JWT
)

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def sanitize(text: str) -> str:
    """Remove credentials from arbitrary log text."""
    cleaned = text
    for index, pattern in enumerate(SECRET_PATTERNS):
        if index == 0:
            cleaned = pattern.sub("sk-***REDACTED***", cleaned)
        elif index == 3:
            cleaned = pattern.sub("***JWT_REDACTED***", cleaned)
        else:
            cleaned = pattern.sub(r"\1***REDACTED***", cleaned)
    return cleaned


class SanitizedFormatter(logging.Formatter):
    """Formatter that scrubs secrets before a record is written."""

    def format(self, record: logging.LogRecord) -> str:
        return sanitize(super().format(record))


def setup_logger(name: str = "jarvis", level: str | None = None) -> logging.Logger:
    log = logging.getLogger(name)
    if log.handlers:
        return log

    log.setLevel(getattr(logging, (level or settings.log_level).upper(), logging.INFO))
    formatter = SanitizedFormatter(LOG_FORMAT, DATE_FORMAT)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    log.addHandler(console)

    try:
        settings.ensure_data_dirs()
        file_handler = RotatingFileHandler(
            settings.logs_dir / "jarvis.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)
    except OSError as exc:  # logging must never prevent startup
        print(f"[logger] file logging disabled ({exc}); continuing with console output")

    log.propagate = False
    return log


def get_logger(name: str = "jarvis") -> logging.Logger:
    return setup_logger(name)


logger = setup_logger()

__all__ = ["logger", "setup_logger", "get_logger", "sanitize", "SanitizedFormatter"]
