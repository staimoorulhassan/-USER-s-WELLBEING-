# Internal API Contracts

**Feature**: User's Wellbeing - Desktop Tracking Application
**Date**: 2025-01-27
**Format**: Service interface definitions (not REST/GraphQL, but Python class interfaces)

## Overview

This document defines the contracts (interfaces) for internal services. These are not web APIs but Python class interfaces that define how components interact.

---

## 1. Tracker Service Interface

**Module**: `services/tracker.py`

```python
class ITrackerService(ABC):
    """Interface for window tracking service."""

    @abstractmethod
    def start_tracking(self) -> None:
        """Begin background window polling.

        Raises:
            RuntimeError: If tracking already active
        """
        pass

    @abstractmethod
    def stop_tracking(self) -> None:
        """Terminate background window polling.

        Raises:
            RuntimeError: If tracking not active
        """
        pass

    @abstractmethod
    def is_tracking(self) -> bool:
        """Check if tracking is currently active.

        Returns:
            bool: True if tracking active, False otherwise
        """
        pass

    @abstractmethod
    def get_recent_activity(self, limit: int = 20) -> List[ActivityLogEntry]:
        """Retrieve recent window activity entries.

        Args:
            limit: Maximum number of entries to return (default: 20)

        Returns:
            List of ActivityLogEntry objects, ordered by timestamp descending

        Raises:
            ValueError: If limit < 1
        """
        pass
```

**Implementation Contract**:
- Must use separate threading.Thread for polling
- Must poll every 5 seconds (configurable in constants.py)
- Must filter browser suffixes using IBrowserFilter
- Must append entries to logs.json atomically
- Must handle Windows exceptions (e.g., window closed during poll)

---

## 2. AI Service Interface

**Module**: `services/ai_service.py`

```python
class IAIService(ABC):
    """Interface for AI-powered insights."""

    @abstractmethod
    def calculate_focus_score(self, activity_logs: List[ActivityLogEntry]) -> float:
        """Calculate focus score from window activity patterns.

        Args:
            activity_logs: List of window activity entries

        Returns:
            Float score 0-100

        Raises:
            TimeoutError: If AI request exceeds 30-second timeout
            APIError: If AI service returns error (rate limit, server error)
            ValueError: If activity_logs is empty
        """
        pass

    @abstractmethod
    def generate_daily_summary(self, activity_logs: List[ActivityLogEntry],
                              profile: UserProfile) -> DailySummary:
        """Generate AI-powered daily summary.

        Args:
            activity_logs: List of window activity entries
            profile: User profile for context (goals, role)

        Returns:
            DailySummary object with insights

        Raises:
            TimeoutError: If AI request exceeds timeout
            APIError: If AI service returns error
            ValueError: If activity_logs empty or profile invalid
        """
        pass

    @abstractmethod
    def detect_task_accomplishments(self, activity_logs: List[ActivityLogEntry],
                                   profile: UserProfile) -> List[str]:
        """Detect completed tasks from activity patterns.

        Args:
            activity_logs: List of window activity entries
            profile: User profile for context

        Returns:
            List of task description strings

        Raises:
            TimeoutError: If AI request exceeds timeout
            APIError: If AI service returns error
        """
        pass
```

**Timeout Behavior**:
- Manual requests: 30-second timeout (calculate_focus_score, generate_daily_summary)
- Shutdown events: 5-second timeout (use shutdown_timeout parameter)

**Error Handling**:
- Must retry once on timeout (exponential backoff: 1s, 2s)
- Must translate API errors to user-friendly messages
- Must preserve local logs even if all retries fail

---

## 3. State Manager Interface

**Module**: `services/state_manager.py`

```python
class IStateManager(ABC):
    """Interface for work state persistence."""

    @abstractmethod
    def save_work_state(self, state: WorkState) -> None:
        """Persist work state to work_state.json.

        Args:
            state: WorkState object to save

        Raises:
            IOError: If file write fails (disk full, permissions)
            ValueError: If state validation fails
        """
        pass

    @abstractmethod
    def load_work_state(self) -> Optional[WorkState]:
        """Load work state from work_state.json.

        Returns:
            WorkState object or None if file doesn't exist

        Raises:
            JSONDecodeError: If file corrupted (return None, log error)
        """
        pass

    @abstractmethod
    def increment_streak(self, current_streak: int,
                        session_productive: bool) -> int:
        """Update streak count based on session productivity.

        Args:
            current_streak: Current streak count
            session_productive: True if session meets productivity criteria

        Returns:
            Updated streak count (0 if session not productive, else current_streak + 1)
        """
        pass
```

**Backup Contract**:
- Must retain .bak files (last 3 versions) on save
- Must restore from backup if corrupted file detected on load

---

## 4. Instance Manager Interface

**Module**: `services/instance_manager.py`

```python
class IInstanceManager(ABC):
    """Interface for single-instance enforcement."""

    @abstractmethod
    def is_first_instance(self) -> bool:
        """Check if this is the first application instance.

        Returns:
            True if first instance, False if another instance running
        """
        pass

    @abstractmethod
    def activate_existing_instance(self) -> None:
        """Bring existing instance window to foreground.

        Raises:
            RuntimeError: If no existing instance found
        """
        pass

    @abstractmethod
    def release_lock(self) -> None:
        """Release instance lock on application shutdown.

        Must be called in atexit handler for crash recovery.
        """
        pass
```

**Platform Implementation**:
- Windows: Named mutex (CreateMutex)
- Fallback: File-based lock (flock)

---

## 5. Event Interceptor Interface

**Module**: `services/event_interceptor.py`

```python
class IEventInterceptor(ABC):
    """Interface for system event interception."""

    @abstractmethod
    def register_shutdown_handler(self, callback: Callable[[], None]) -> None:
        """Register callback for shutdown/sleep events.

        Args:
            callback: Function to call before shutdown
                     Must return quickly (max 5 seconds)
        """
        pass

    @abstractmethod
    def block_shutdown(self, timeout_seconds: int = 5) -> None:
        """Block system shutdown to show user prompt.

        Args:
            timeout_seconds: Maximum time to block (default: 5)

        Raises:
            RuntimeError: If called from non-UI thread
        """
        pass

    @abstractmethod
    def allow_shutdown(self) -> None:
        """Allow system shutdown to proceed.

        Must be called after user responds to prompt.
        """
        pass
```

**Windows Implementation**:
- Use WM_QUERYENDSESSION message handler
- Return False to block shutdown temporarily
- Must complete within timeout (Windows enforces 5-second limit)

---

## 6. File Handler Interface

**Module**: `utils/file_handler.py`

```python
class IFileHandler(ABC):
    """Interface for atomic JSON file operations."""

    @abstractmethod
    def read_json(self, filepath: str) -> Dict[str, Any]:
        """Read JSON file with atomic operation.

        Args:
            filepath: Path to JSON file

        Returns:
            Parsed JSON as dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            JSONDecodeError: If file corrupted (try backup recovery)
        """
        pass

    @abstractmethod
    def write_json(self, filepath: str, data: Dict[str, Any]) -> None:
        """Write JSON file atomically.

        Args:
            filepath: Path to JSON file
            data: Dictionary to write

        Raises:
            IOError: If write fails (disk full, permissions)

        Side effects:
            - Creates backup (.bak) before overwriting
            - Rotates backups (keeps last 3 versions)
        """
        pass

    @abstractmethod
    def restore_from_backup(self, filepath: str) -> bool:
        """Attempt to restore file from backup.

        Args:
            filepath: Path to corrupted file

        Returns:
            True if restore successful, False otherwise
        """
        pass
```

**Atomic Write Pattern**:
1. Write to temporary file (.tmp)
2. fsync() to flush to disk
3. os.replace() for atomic rename
4. Cleanup .tmp file on error

---

## 7. Browser Filter Interface

**Module**: `utils/browser_filters.py`

```python
class IBrowserFilter(ABC):
    """Interface for browser suffix filtering."""

    @abstractmethod
    def filter(self, window_title: str) -> str:
        """Remove browser suffix from window title.

        Args:
            window_title: Raw window title (e.g., "GitHub - Google Chrome")

        Returns:
            Filtered title (e.g., "GitHub")

        Examples:
            >>> filter("GitHub - Google Chrome")
            "GitHub"
            >>> filter("Visual Studio Code")
            "Visual Studio Code" (unchanged, not a browser)
        """
        pass

    @abstractmethod
    def add_custom_suffix(self, suffix: str) -> None:
        """Add custom browser suffix pattern.

        Args:
            suffix: Suffix to filter (e.g., " - MyCustomBrowser")

        Raises:
            ValueError: If suffix empty or invalid regex
        """
        pass
```

**Default Patterns**:
```python
DEFAULT_SUFFIXES = [
    r" - Google Chrome$",
    r" - Mozilla Firefox$",
    r" - Microsoft Edge$",
    r" - Brave$",
    r" - Opera$",
    r" - Vivaldi$"
]
```

---

## 8. Notification Manager Interface

**Module**: `ui/notifications.py`

```python
class INotificationManager(ABC):
    """Interface for user notifications."""

    @abstractmethod
    def show_task_celebration(self, task_description: str) -> None:
        """Show celebratory notification for task completion.

        Args:
            task_description: Task that was completed

        Animation:
            - Star flash animation in center of screen
            - Auto-dismiss after 5 seconds
            - Click to dismiss immediately
        """
        pass

    @abstractmethod
    def show_shutdown_prompt(self) -> bool:
        """Show shutdown summary prompt.

        Returns:
            True if user wants summary before shutdown, False otherwise

        Dialog:
            - "Generate summary before shutdown?"
            - Yes (generate summary, then shutdown)
            - No (shutdown immediately)
            - Timeout after 5 seconds (default to No)
        """
        pass

    @abstractmethod
    def show_error(self, message: str) -> None:
        """Show error notification.

        Args:
            message: User-friendly error message

        Style:
            - Red background
            - Auto-dismiss after 10 seconds
            - Log to file for debugging
        """
        pass
```

---

## Error Handling Contracts

### Exceptions Hierarchy

```python
class WellbeingError(Exception):
    """Base exception for application errors."""
    pass

class TrackerError(WellbeingError):
    """Raised when tracker service fails."""
    pass

class AIServiceError(WellbeingError):
    """Raised when AI service call fails."""
    pass

class DataCorruptionError(WellbeingError):
    """Raised when JSON file is corrupted."""
    pass

class InstanceError(WellbeingError):
    """Raised when instance management fails."""
    pass
```

### Error Translation

All services must translate technical exceptions to user-friendly messages:

```python
try:
    ai_service.generate_daily_summary(logs, profile)
except TimeoutError:
    notification_manager.show_error(
        "AI service timed out. Please check your internet connection and try again."
    )
except APIError as e:
    if e.status_code == 429:
        notification_manager.show_error(
            "AI service rate limit exceeded. Please wait a moment and try again."
        )
    else:
        notification_manager.show_error(
            "Unable to generate summary. Your logs have been saved locally."
        )
```

---

## Testing Contracts

### Mock Interfaces for Testing

All interfaces must be mockable for unit tests:

```python
# Example test with mocked AI service
@patch('services.ai_service.AIService')
def test_focus_score_calculation(mock_ai_service):
    # Configure mock
    mock_ai_service.calculate_focus_score.return_value = 75.0

    # Test
    result = ai_service.calculate_focus_score(mock_logs)

    # Assert
    assert result == 75.0
    mock_ai_service.calculate_focus_score.assert_called_once_with(mock_logs)
```

---

## Summary

These internal API contracts define how services interact within the application. All implementations must adhere to these interfaces for testability, maintainability, and clear separation of concerns.

**Key Principles**:
- All services mockable for testing
- Clear error handling contracts
- Platform-specific details abstracted
- Atomic operations for data integrity
- User-friendly error messages

**Next Step**: Implement these contracts following the order in [quickstart.md](./quickstart.md) Phase 1-4 tasks.
