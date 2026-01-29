"""Work state model for session persistence and streak tracking.

Stores work session data across application launches.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class WorkState:
    """Represents the work state across sessions.

    Attributes:
        session_summary: Summary of the last work session
        completed_tasks: List of tasks completed during the session
        timestamp: ISO format timestamp of when the state was last updated
        streak_count: Number of consecutive productive sessions
        last_productive_session: ISO timestamp of last productive session, or None
        focus_score: Focus score from last session (0-100), or None
        total_tracking_minutes: Total minutes tracked in the session
    """

    session_summary: str
    completed_tasks: list[str]
    timestamp: str
    streak_count: int = 0
    last_productive_session: Optional[str] = None
    focus_score: Optional[int] = None
    total_tracking_minutes: int = 0

    def __post_init__(self):
        """Validate work state data after initialization."""
        # Validate streak_count
        if self.streak_count < 0:
            raise ValueError("streak_count must be >= 0")

        # Validate total_tracking_minutes
        if self.total_tracking_minutes < 0:
            raise ValueError("total_tracking_minutes must be >= 0")

        # Validate focus_score if present
        if self.focus_score is not None:
            if not (0 <= self.focus_score <= 100):
                raise ValueError("focus_score must be between 0 and 100")

    def to_dict(self) -> dict:
        """Convert work state to dictionary for JSON serialization.

        Returns:
            Dictionary representation of work state
        """
        return {
            "session_summary": self.session_summary,
            "completed_tasks": self.completed_tasks,
            "timestamp": self.timestamp,
            "streak_count": self.streak_count,
            "last_productive_session": self.last_productive_session,
            "focus_score": self.focus_score,
            "total_tracking_minutes": self.total_tracking_minutes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkState":
        """Create WorkState from dictionary.

        Args:
            data: Dictionary containing work state data

        Returns:
            WorkState instance

        Raises:
            KeyError: If required fields are missing
            ValueError: If data validation fails
        """
        try:
            return cls(
                session_summary=data["session_summary"],
                completed_tasks=data["completed_tasks"],
                timestamp=data["timestamp"],
                streak_count=data.get("streak_count", 0),
                last_productive_session=data.get("last_productive_session"),
                focus_score=data.get("focus_score"),
                total_tracking_minutes=data.get("total_tracking_minutes", 0),
            )
        except KeyError as e:
            raise KeyError(f"Missing required field in work state data: {e}") from e

    @classmethod
    def create_empty(cls) -> "WorkState":
        """Create an empty work state for first-time users.

        Returns:
            WorkState with default/empty values
        """
        return cls(
            session_summary="",
            completed_tasks=[],
            timestamp=datetime.now().isoformat(),
            streak_count=0,
            last_productive_session=None,
            focus_score=None,
            total_tracking_minutes=0,
        )
