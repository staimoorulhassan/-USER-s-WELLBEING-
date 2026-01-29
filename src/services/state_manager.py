"""State manager for work state persistence and streak tracking.

Handles saving, loading, and updating work state across sessions.
"""

import logging
from typing import Optional

from config.constants import (
    MIN_FOCUS_SCORE,
    MIN_PRODUCTIVE_SESSION_MINUTES,
    WORK_STATE_FILE,
)
from models.work_state import WorkState
from utils.file_handler import read_json, write_json
from services.tracker import TrackerService
from services.profile_service import ProfileService

logger = logging.getLogger(__name__)


class StateManager:
    """Service for managing work state operations."""

    def __init__(self, work_state_path=None):
        """Initialize state manager.

        Args:
            work_state_path: Custom work state file path (defaults to WORK_STATE_FILE)
        """
        self.work_state_path = work_state_path or WORK_STATE_FILE

    def load_work_state(self) -> Optional[WorkState]:
        """Load work state from file.

        Returns:
            WorkState instance if file exists and is valid
            None if file doesn't exist

        Raises:
            ValueError: If work state file is corrupted
        """
        data = read_json(self.work_state_path)

        if data is None:
            logger.info(f"No work state file found at {self.work_state_path}")
            return None

        try:
            work_state = WorkState.from_dict(data)
            logger.info(f"Successfully loaded work state (streak: {work_state.streak_count})")
            return work_state
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse work state: {e}")
            raise ValueError(f"Invalid work state data: {e}") from e

    def save_work_state(self, work_state: WorkState) -> None:
        """Save work state to file.

        Args:
            work_state: WorkState instance to save

        Raises:
            FileHandlerError: If file write fails
        """
        # Update timestamp before saving
        work_state.timestamp = work_state.timestamp or WorkState.create_empty().timestamp

        # Save to file (atomic write with backup)
        write_json(self.work_state_path, work_state.to_dict())
        logger.info(f"Work state saved to {self.work_state_path}")

    def increment_streak(self, current_streak: int) -> int:
        """Increment streak count.

        Args:
            current_streak: Current streak count

        Returns:
            New streak count (incremented by 1)
        """
        new_streak = current_streak + 1
        logger.info(f"Streak incremented: {current_streak} -> {new_streak}")
        return new_streak

    def reset_streak(self) -> int:
        """Reset streak count to zero.

        Returns:
            New streak count (0)
        """
        logger.info("Streak reset to 0")
        return 0

    def determine_productive_session(
        self,
        tracking_minutes: int,
        focus_score: Optional[int],
        completed_tasks: list[str],
    ) -> bool:
        """Determine if a session was productive.

        Productive session criteria:
        - tracking_minutes >= 30 (MIN_PRODUCTIVE_SESSION_MINUTES)
        - focus_score >= 50 (MIN_FOCUS_SCORE) if available
        - completed_tasks length >= 1

        Args:
            tracking_minutes: Total minutes tracked in session
            focus_score: Focus score from session (0-100), or None
            completed_tasks: List of completed tasks

        Returns:
            True if session was productive, False otherwise
        """
        # Check minimum tracking time
        if tracking_minutes < MIN_PRODUCTIVE_SESSION_MINUTES:
            logger.info(
                f"Session not productive: tracking time ({tracking_minutes} min) "
                f"< minimum ({MIN_PRODUCTIVE_SESSION_MINUTES} min)"
            )
            return False

        # Check focus score if available
        if focus_score is not None and focus_score < MIN_FOCUS_SCORE:
            logger.info(
                f"Session not productive: focus score ({focus_score}) "
                f"< minimum ({MIN_FOCUS_SCORE})"
            )
            return False

        # Check completed tasks
        if len(completed_tasks) < 1:
            logger.info("Session not productive: no completed tasks")
            return False

        logger.info("Session marked as productive")
        return True

    def update_streak_if_productive(
        self,
        work_state: WorkState,
        is_productive: bool,
        session_timestamp: str,
    ) -> WorkState:
        """Update streak count based on productivity.

        Args:
            work_state: Current work state
            is_productive: Whether the session was productive
            session_timestamp: ISO timestamp of current session

        Returns:
            Updated work state
        """
        if is_productive:
            work_state.streak_count = self.increment_streak(work_state.streak_count)
            work_state.last_productive_session = session_timestamp
            logger.info(f"Productive session! Streak: {work_state.streak_count}")
        else:
            logger.info("Session not productive - streak not incremented")
            # Keep existing streak count but don't update last_productive_session

        return work_state

    def determine_work_state(self, tracker_service: TrackerService, profile_service: ProfileService) -> WorkState:
        """Determine work state from current tracker session.

        Args:
            tracker_service: Current tracker service instance
            profile_service: Profile service for user data

        Returns:
            WorkState instance with current session data
        """
        try:
            # Get tracking data
            session_stats = tracker_service.get_session_stats()
            tracking_minutes = session_stats["tracking_minutes"]
            focus_score = session_stats["focus_score"]
            activity_count = session_stats["activity_count"]

            # Get completed tasks (placeholder - would need AI detection)
            completed_tasks = []  # TODO: Implement task detection

            # Create work state
            work_state = WorkState.create_empty()
            work_state.tracking_minutes = tracking_minutes
            work_state.activity_count = activity_count
            work_state.focus_score = focus_score
            work_state.completed_tasks = completed_tasks
            work_state.session_summary = f"Session tracked for {tracking_minutes} minutes with {activity_count} activities"

            # Determine if productive
            is_productive = self.determine_productive_session(
                tracking_minutes,
                focus_score,
                completed_tasks
            )

            if is_productive:
                work_state = self.update_streak_if_productive(
                    work_state,
                    is_productive,
                    work_state.timestamp
                )

            return work_state

        except Exception as e:
            logger.error(f"Failed to determine work state: {e}")
            # Return empty state on error
            return WorkState.create_empty()
