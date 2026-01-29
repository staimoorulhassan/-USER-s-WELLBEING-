"""ActivityLogEntry model for tracking window activity.

Records window title changes with timestamps and application info.
"""

from datetime import datetime
from typing import Optional


class ActivityLogEntry:
    """Single activity log entry representing a window state."""

    def __init__(
        self,
        timestamp: datetime,
        window_title: str,
        raw_window_title: str,
        application: str,
        duration_seconds: int = 0,
    ):
        """Initialize activity log entry.

        Args:
            timestamp: When this window was active
            window_title: Filtered window title (browser suffixes removed)
            raw_window_title: Original window title from OS
            application: Application name (e.g., "Chrome", "Firefox")
            duration_seconds: How long this window was active (computed later)
        """
        self.timestamp = timestamp
        self.window_title = window_title
        self.raw_window_title = raw_window_title
        self.application = application
        self.duration_seconds = duration_seconds

    def to_dict(self) -> dict:
        """Convert entry to dictionary for JSON serialization.

        Returns:
            Dictionary representation
        """
        return {
            "timestamp": self.timestamp.isoformat(),
            "window_title": self.window_title,
            "raw_window_title": self.raw_window_title,
            "application": self.application,
            "duration_seconds": self.duration_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ActivityLogEntry":
        """Create entry from dictionary (deserialization).

        Args:
            data: Dictionary with entry data

        Returns:
            ActivityLogEntry instance
        """
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            window_title=data["window_title"],
            raw_window_title=data["raw_window_title"],
            application=data["application"],
            duration_seconds=data.get("duration_seconds", 0),
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"ActivityLogEntry(timestamp={self.timestamp}, "
            f"window_title='{self.window_title}', "
            f"application='{self.application}')"
        )
