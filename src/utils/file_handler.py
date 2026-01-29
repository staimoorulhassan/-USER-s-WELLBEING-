"""Atomic JSON file handler with backup support.

Provides crash-safe file operations using atomic writes (tempfile + os.replace).
Implements automatic backup rotation for data safety.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Any, Optional
import logging

from config.constants import BACKUP_COUNT

logger = logging.getLogger(__name__)


class FileHandlerError(Exception):
    """Base exception for file handler operations."""
    pass


class DataCorruptionError(FileHandlerError):
    """Raised when file content is corrupted or invalid."""
    pass


def read_json(file_path: Path) -> Optional[dict[str, Any]]:
    """Read and parse a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data as dictionary, or None if file doesn't exist

    Raises:
        DataCorruptionError: If file exists but contains invalid JSON
        FileHandlerError: If file cannot be read (permissions, etc.)
    """
    if not file_path.exists():
        logger.debug(f"File does not exist: {file_path}")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug(f"Successfully read JSON from {file_path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        raise DataCorruptionError(f"Corrupted JSON file: {file_path}") from e
    except OSError as e:
        logger.error(f"Failed to read {file_path}: {e}")
        raise FileHandlerError(f"Cannot read file: {file_path}") from e


def write_json(file_path: Path, data: dict[str, Any]) -> None:
    """Write data to JSON file using atomic write pattern.

    Creates a temporary file, writes to it, then atomically replaces
    the target file. This prevents corruption if write is interrupted.

    Also creates a backup of the previous file if it exists.

    Args:
        file_path: Target file path
        data: Dictionary data to write as JSON

    Raises:
        FileHandlerError: If write operation fails
    """
    # Create parent directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Create backup of existing file
    if file_path.exists():
        _create_backup(file_path)

    # Write to temporary file
    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except (OSError, TypeError) as e:
        logger.error(f"Failed to write temporary file {temp_path}: {e}")
        # Clean up temp file if it exists
        if temp_path.exists():
            temp_path.unlink()
        raise FileHandlerError(f"Failed to write file: {file_path}") from e

    # Atomic replace (works on Windows and Unix)
    try:
        os.replace(temp_path, file_path)
        logger.debug(f"Successfully wrote JSON to {file_path}")
    except OSError as e:
        logger.error(f"Failed to replace {file_path}: {e}")
        # Clean up temp file if replace failed
        if temp_path.exists():
            temp_path.unlink()
        raise FileHandlerError(f"Failed to save file: {file_path}") from e


def _create_backup(file_path: Path) -> None:
    """Create rotated backup of the file.

    Maintains BACKUP_COUNT versions:
    - file.json -> file.json.bak
    - file.json.bak -> file.json.bak.1
    - file.json.bak.1 -> file.json.bak.2
    - file.json.bak.2 -> file.json.bak.3 (removed if BACKUP_COUNT=3)

    Args:
        file_path: File to backup
    """
    if not file_path.exists():
        return

    # Shift existing backups
    for i in range(BACKUP_COUNT - 1, 0, -1):
        old_backup = file_path.with_suffix(f"{file_path.suffix}.bak.{i}")
        new_backup = file_path.with_suffix(f"{file_path.suffix}.bak.{i + 1}")
        if old_backup.exists():
            shutil.move(str(old_backup), str(new_backup))

    # Move .bak to .bak.1
    backup_path = file_path.with_suffix(f"{file_path.suffix}.bak")
    if backup_path.exists():
        shutil.move(str(backup_path), str(file_path.with_suffix(f"{file_path.suffix}.bak.1")))

    # Create new backup from current file
    shutil.copy2(str(file_path), str(backup_path))
    logger.debug(f"Created backup: {backup_path}")


def restore_from_backup(file_path: Path) -> bool:
    """Attempt to restore a file from its backups.

    Tries backups in order: .bak, .bak.1, .bak.2, .bak.3

    Args:
        file_path: Corrupted file path

    Returns:
        True if restore succeeded, False otherwise
    """
    backup_candidates = [
        file_path.with_suffix(f"{file_path.suffix}.bak"),
        file_path.with_suffix(f"{file_path.suffix}.bak.1"),
        file_path.with_suffix(f"{file_path.suffix}.bak.2"),
        file_path.with_suffix(f"{file_path.suffix}.bak.3"),
    ]

    for backup in backup_candidates:
        if backup.exists():
            try:
                shutil.copy2(str(backup), str(file_path))
                logger.info(f"Restored {file_path} from backup: {backup}")
                return True
            except OSError as e:
                logger.warning(f"Failed to restore from backup {backup}: {e}")
                continue

    logger.error(f"No valid backup found for {file_path}")
    return False


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in megabytes.

    Args:
        file_path: File to check

    Returns:
        File size in MB (0 if file doesn't exist)
    """
    if not file_path.exists():
        return 0.0
    return file_path.stat().st_size / (1024 * 1024)
