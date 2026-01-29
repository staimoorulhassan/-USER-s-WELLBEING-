"""Logs.json file structure handler.

Manages activity logs file with entries array and metadata.
"""

import logging
from typing import List, Optional
from datetime import datetime

from config.constants import LOGS_FILE, LOG_SIZE_LIMIT_MB
from models.activity_log import ActivityLogEntry
from utils.file_handler import read_json, write_json, get_file_size_mb

logger = logging.getLogger(__name__)


class LogHandler:
    """Handler for logs.json file operations."""

    def __init__(self, log_path=None):
        """Initialize log handler.

        Args:
            log_path: Custom log file path (defaults to LOGS_FILE)
        """
        self.log_path = log_path or LOGS_FILE

    def initialize_log_file(self) -> None:
        """Create new logs.json file with empty structure."""
        initial_data = {
            "entries": [],
            "metadata": {
                "version": "1.0",
                "total_entries": 0,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
            },
        }

        write_json(self.log_path, initial_data)
        logger.info(f"Initialized log file: {self.log_path}")

    def append_entry(self, entry: ActivityLogEntry) -> None:
        """Append a new activity log entry.

        Args:
            entry: ActivityLogEntry to append
        """
        # Read existing data or initialize new file
        data = read_json(self.log_path)
        if data is None:
            self.initialize_log_file()
            data = read_json(self.log_path)

        # Append entry
        data["entries"].append(entry.to_dict())

        # Update metadata
        data["metadata"]["total_entries"] = len(data["entries"])
        data["metadata"]["last_updated"] = datetime.now().isoformat()

        # Write back to file
        write_json(self.log_path, data)

        logger.debug(f"Appended log entry: {entry.window_title}")

    def get_entries(self, limit: Optional[int] = None) -> List[dict]:
        """Get log entries.

        Args:
            limit: Maximum number of entries to return (most recent first)

        Returns:
            List of entry dictionaries
        """
        data = read_json(self.log_path)
        if data is None:
            return []

        entries = data.get("entries", [])

        # Sort by timestamp descending (most recent first)
        entries.sort(key=lambda e: e["timestamp"], reverse=True)

        # Apply limit if specified
        if limit:
            entries = entries[:limit]

        return entries

    def get_all_entries(self) -> List[dict]:
        """Get all log entries in chronological order.

        Returns:
            List of entry dictionaries (oldest to newest)
        """
        data = read_json(self.log_path)
        if data is None:
            return []

        entries = data.get("entries", [])

        # Sort by timestamp ascending (oldest first)
        entries.sort(key=lambda e: e["timestamp"])

        return entries

    def manage_file_size(self) -> bool:
        """Check and manage log file size.

        If file exceeds LOG_SIZE_LIMIT_MB, this could:
        - Log a warning
        - Trigger cleanup
        - Notify user

        Returns:
            True if file size is acceptable, False if it exceeds limit
        """
        size_mb = get_file_size_mb(self.log_path)

        if size_mb > LOG_SIZE_LIMIT_MB:
            logger.warning(
                f"Log file size ({size_mb:.1f}MB) exceeds limit ({LOG_SIZE_LIMIT_MB}MB)"
            )
            return False

        if size_mb > LOG_SIZE_LIMIT_MB * 0.8:
            logger.warning(
                f"Log file size ({size_mb:.1f}MB) approaching limit ({LOG_SIZE_LIMIT_MB}MB)"
            )

        return True

    def get_metadata(self) -> dict:
        """Get log file metadata.

        Returns:
            Metadata dictionary or empty dict if file doesn't exist
        """
        data = read_json(self.log_path)
        if data is None:
            return {}

        return data.get("metadata", {})

    def clear_entries(self) -> None:
        """Clear all log entries (keep metadata)."""
        data = read_json(self.log_path)
        if data is None:
            self.initialize_log_file()
            return

        data["entries"] = []
        data["metadata"]["total_entries"] = 0
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        data["metadata"]["last_cleared"] = datetime.now().isoformat()

        write_json(self.log_path, data)
        logger.info("Cleared all log entries")
