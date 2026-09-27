"""Structured local logging for the JARVIS runtime.

Logs are written to `%LOCALAPPDATA%\\Jarvis\\logs\\jarvis.log` with rotation.
A sanitising formatter scrubs API keys, bearer tokens and secret assignments so
credentials never reach the log files.
"""

from .logger import get_logger, logger, setup_logger

__all__ = ["logger", "setup_logger", "get_logger"]
