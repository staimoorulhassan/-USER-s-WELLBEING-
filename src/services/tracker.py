"""Tracker service for background window activity monitoring.

Uses background thread to poll active window every 5 seconds.
Integrates with pywin32 for Windows API access.
"""

import logging
import threading
import time
from datetime import datetime
from typing import Optional, List

try:
    import win32gui
except ImportError:
    win32gui = None
    logging.warning("pywin32 not available - tracker will not function")

from config.constants import (
    LOGS_FILE,
    POLLING_INTERVAL_SECONDS,
    MAX_LIVE_FEED_ENTRIES,
)
from models.activity_log import ActivityLogEntry
from models.work_state import WorkState
from utils.log_handler import LogHandler
from utils.browser_filters import BrowserFilter
from utils.exceptions import TrackerError

try:
    from services.state_manager import StateManager
except ImportError:
    StateManager = None
    logging.warning("StateManager not available - work state persistence disabled")

logger = logging.getLogger(__name__)


class TrackerService:
    """Background window activity tracker."""

    def __init__(self, log_path=None):
        """Initialize tracker service.

        Args:
            log_path: Custom log file path (defaults to LOGS_FILE)
        """
        if win32gui is None:
            raise TrackerError("pywin32 is required for tracker functionality")

        self.log_handler = LogHandler(log_path)
        self.browser_filter = BrowserFilter()

        # State manager for work state persistence
        self.state_manager = StateManager() if StateManager else None

        # Threading controls
        self.tracking_thread: Optional[threading.Thread] = None
        self.tracking_event = threading.Event()

        # State tracking
        self._is_tracking = False
        self._last_window_title: Optional[str] = None
        self._last_timestamp: Optional[datetime] = None
        self._session_start_time: Optional[datetime] = None

        # Activity buffer for live feed (in-memory, most recent entries)
        self.activity_buffer: List[ActivityLogEntry] = []

        # Session data for work state
        self._session_focus_score: Optional[int] = None

        # Initialize log file if needed
        if not self.log_handler.log_path.exists():
            self.log_handler.initialize_log_file()

    def start_tracking(self) -> None:
        """Start background tracking thread."""
        if self._is_tracking:
            logger.warning("Tracking already in progress")
            return

        self._is_tracking = True
        self.tracking_event.clear()
        self._session_start_time = datetime.now()
        self._session_focus_score = None

        # Create and start daemon thread
        self.tracking_thread = threading.Thread(
            target=self._polling_loop, daemon=True, name="TrackerThread"
        )
        self.tracking_thread.start()

        logger.info("Tracking started")

    def stop_tracking(self) -> None:
        """Stop background tracking thread and save work state."""
        if not self._is_tracking:
            logger.warning("Tracking not in progress")
            return

        self._is_tracking = False
        self.tracking_event.set()

        # Wait for thread to finish (with timeout)
        if self.tracking_thread and self.tracking_thread.is_alive():
            self.tracking_thread.join(timeout=2.0)

        # Save work state
        self._save_work_state()

        logger.info("Tracking stopped")

    def set_session_focus_score(self, score: int) -> None:
        """Set the focus score for the current session.

        Args:
            score: Focus score value (0-100)
        """
        self._session_focus_score = score
        logger.debug(f"Session focus score set to {score}")

    def get_session_stats(self) -> dict:
        """Get statistics for the current session.

        Returns:
            Dictionary with session statistics including:
            - tracking_minutes: Total minutes tracked
            - focus_score: Session focus score (if available)
            - activity_count: Number of activity entries logged
        """
        tracking_minutes = 0
        if self._session_start_time:
            elapsed = datetime.now() - self._session_start_time
            tracking_minutes = int(elapsed.total_seconds() / 60)

        return {
            "tracking_minutes": tracking_minutes,
            "focus_score": self._session_focus_score,
            "activity_count": len(self.activity_buffer),
        }

    def _save_work_state(self) -> None:
        """Save work state on session end.

        Calculates session statistics and saves work state file.
        """
        if not self.state_manager:
            logger.debug("StateManager not available - skipping work state save")
            return

        try:
            # Get session stats
            stats = self.get_session_stats()
            tracking_minutes = stats["tracking_minutes"]

            # Generate session summary
            session_summary = self._generate_session_summary(stats)

            # Load existing work state to preserve streak
            existing_state = self.state_manager.load_work_state()
            if existing_state:
                streak_count = existing_state.streak_count
            else:
                streak_count = 0

            # Determine if session was productive
            is_productive = self.state_manager.determine_productive_session(
                tracking_minutes=tracking_minutes,
                focus_score=self._session_focus_score,
                completed_tasks=[],  # Will be populated by task detection in Phase 11
            )

            # Update streak
            session_timestamp = datetime.now().isoformat()
            if existing_state:
                work_state = self.state_manager.update_streak_if_productive(
                    existing_state, is_productive, session_timestamp
                )
            else:
                work_state = WorkState.create_empty()
                work_state.streak_count = 1 if is_productive else 0
                work_state.last_productive_session = session_timestamp if is_productive else None

            # Update work state with session data
            work_state.session_summary = session_summary
            work_state.completed_tasks = []  # Will be populated by task detection in Phase 11
            work_state.focus_score = self._session_focus_score
            work_state.total_tracking_minutes = tracking_minutes
            work_state.timestamp = session_timestamp

            # Save work state
            self.state_manager.save_work_state(work_state)
            logger.info("Work state saved on session end")

        except Exception as e:
            logger.error(f"Failed to save work state: {e}", exc_info=True)

    def _generate_session_summary(self, stats: dict) -> str:
        """Generate a summary of the current session.

        Args:
            stats: Session statistics dictionary

        Returns:
            Session summary string
        """
        tracking_minutes = stats["tracking_minutes"]
        activity_count = stats["activity_count"]

        if tracking_minutes < 1:
            return "Very short session (< 1 minute)"

        hours = tracking_minutes // 60
        minutes = tracking_minutes % 60

        if hours > 0:
            duration_str = f"{hours}h {minutes}m"
        else:
            duration_str = f"{minutes}m"

        return f"Tracked for {duration_str} with {activity_count} activities logged"

    def is_tracking(self) -> bool:
        """Check if tracking is currently active.

        Returns:
            True if tracking is active
        """
        return self._is_tracking

    def get_recent_activity(self, limit: int = MAX_LIVE_FEED_ENTRIES) -> List[ActivityLogEntry]:
        """Get recent activity entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of recent ActivityLogEntry objects
        """
        return self.activity_buffer[:limit]

    def get_activity_count(self) -> int:
        """Get total number of activity entries in buffer.

        Returns:
            Count of activity entries
        """
        return len(self.activity_buffer)

    def _polling_loop(self) -> None:
        """Main polling loop (runs in background thread)."""
        logger.debug("Polling loop started")

        while self._is_tracking and not self.tracking_event.is_set():
            try:
                # Capture current window
                raw_title = self._get_active_window_title()

                if raw_title:
                    # Filter browser suffixes
                    filtered_title = self.browser_filter.filter(raw_title)

                    # Log if window changed
                    if self._should_log_window(filtered_title):
                        self._log_window_activity(filtered_title, raw_title)

            except Exception as e:
                logger.error(f"Error in polling loop: {e}", exc_info=True)

            # Wait for polling interval or stop event
            self.tracking_event.wait(timeout=POLLING_INTERVAL_SECONDS)

        logger.debug("Polling loop ended")

    def _get_active_window_title(self) -> str:
        """Get title of currently active window.

        Returns:
            Window title or empty string on error
        """
        try:
            foreground_window = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(foreground_window)
            return title or ""
        except Exception as e:
            logger.error(f"Failed to get window title: {e}")
            return ""

    def _get_filtered_window_title(self) -> str:
        """Get filtered window title (browser suffixes removed).

        Returns:
            Filtered window title
        """
        raw_title = self._get_active_window_title()
        return self.browser_filter.filter(raw_title)

    def _should_log_window(self, window_title: str) -> bool:
        """Determine if window should be logged.

        Args:
            window_title: Current window title

        Returns:
            True if window should be logged
        """
        # Don't log empty titles
        if not window_title or not window_title.strip():
            return False

        # Don't log if same as last window
        if self._last_window_title == window_title:
            return False

        return True

    def _log_window_activity(self, filtered_title: str, raw_title: str) -> None:
        """Log window activity to file and buffer.

        Args:
            filtered_title: Filtered window title
            raw_title: Original window title
        """
        now = datetime.now()

        # Calculate duration for previous window
        duration_seconds = 0
        if self._last_timestamp:
            duration_seconds = int((now - self._last_timestamp).total_seconds())

        # Extract application name
        application = self._extract_application(raw_title)

        # Create entry
        entry = ActivityLogEntry(
            timestamp=now,
            window_title=filtered_title,
            raw_window_title=raw_title,
            application=application,
            duration_seconds=duration_seconds,
        )

        # Update previous window's duration
        if len(self.activity_buffer) > 0:
            self.activity_buffer[0].duration_seconds = duration_seconds

        # Add to buffer (most recent first)
        self.activity_buffer.insert(0, entry)

        # Keep buffer size limited
        if len(self.activity_buffer) > MAX_LIVE_FEED_ENTRIES:
            self.activity_buffer = self.activity_buffer[:MAX_LIVE_FEED_ENTRIES]

        # Write to log file
        try:
            self.log_handler.append_entry(entry)
            logger.debug(f"Logged window: {filtered_title}")
        except Exception as e:
            logger.error(f"Failed to write log entry: {e}")

        # Update state
        self._last_window_title = filtered_title
        self._last_timestamp = now

    def _extract_application(self, window_title: str) -> str:
        """Extract application name from window title.

        Args:
            window_title: Raw window title

        Returns:
            Application name (e.g., "Chrome", "Firefox", "VSCode")
        """
        # Check for browser suffixes
        if "Google Chrome" in window_title:
            return "Chrome"
        elif "Mozilla Firefox" in window_title:
            return "Firefox"
        elif "Microsoft Edge" in window_title:
            return "Edge"
        elif "Brave" in window_title:
            return "Brave"
        elif "Opera" in window_title:
            return "Opera"
        elif "Vivaldi" in window_title:
            return "Vivaldi"
        else:
            # For non-browsers, use generic name
            # Could be enhanced to detect common apps
            return "Desktop"
