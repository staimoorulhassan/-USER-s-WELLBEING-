"""Structured logging configuration for Wellbeing application.

Provides RotatingFileHandler for automatic log rotation,
with both file and console handlers.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from config.constants import WELLBEING_DIR


def setup_logging(
    name: str = "wellbeing",
    log_level: int = logging.INFO,
    log_to_file: bool = True,
    log_to_console: bool = True,
) -> logging.Logger:
    """Setup structured logging with file rotation.

    Creates logs directory in ~/.wellbeing/logs/ if it doesn't exist.
    Uses RotatingFileHandler to automatically rotate logs at 5MB.

    Args:
        name: Logger name
        log_level: Logging level (default: INFO)
        log_to_file: Enable file logging
        log_to_console: Enable console logging

    Returns:
        Configured logger instance
    """
    # Configure root logger to capture all logs
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler with rotation
    if log_to_file:
        log_dir = WELLBEING_DIR / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{name}.log"

        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


# Create default logger
default_logger = setup_logging()
