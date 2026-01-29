"""Task accomplishment detection service.

Uses AI to detect when users complete tasks based on their activity patterns.
"""

import logging
import threading
import time
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
import json

from models.activity_log import ActivityLogEntry
from models.ai_models import DailySummary
from services.ai_service import AIService
from utils.log_handler import LogHandler

logger = logging.getLogger(__name__)


class TaskAccomplishment:
    """Represents a detected task accomplishment."""

    def __init__(self, task_name: str, confidence: float, timestamp: str,
                 activity_window: List[ActivityLogEntry], context: str = ""):
        """Initialize task accomplishment.

        Args:
            task_name: Name or description of the accomplished task
            confidence: Confidence score (0-1) that this is a valid task completion
            timestamp: ISO timestamp of when task was completed
            activity_window: List of activities around the task completion
            context: Additional context about the task accomplishment
        """
        self.task_name = task_name
        self.confidence = confidence
        self.timestamp = timestamp
        self.activity_window = activity_window
        self.context = context

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "task_name": self.task_name,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "context": self.context,
            "activity_count": len(self.activity_window)
        }


class TaskDetectionService:
    """Service for detecting task accomplishments using AI."""

    def __init__(self):
        """Initialize task detection service."""
        self.ai_service = AIService()
        self.log_handler = LogHandler()
        self.detection_callback: Optional[Callable[[TaskAccomplishment], None]] = None

        # Detection configuration
        self.window_size_minutes = 10  # Look at 10-minute windows
        self.min_confidence = 0.7  # Minimum confidence to trigger celebration
        self.cooldown_period = 300  # 5 minutes between celebrations

        # State tracking
        self.last_detection_time = None
        self.is_running = False
        self.detection_thread = None
        self.stop_event = threading.Event()

        # Queue system
        self.detection_queue: List[TaskAccomplishment] = []
        self.queue_lock = threading.Lock()
        self.max_queue_size = 10
        self.queue_check_interval = 60  # Check queue every minute

    def set_detection_callback(self, callback: Callable[[TaskAccomplishment], None]) -> None:
        """Set callback for when tasks are detected.

        Args:
            callback: Function to call when task is detected
        """
        self.detection_callback = callback

    def start_detection(self) -> None:
        """Start task detection in background."""
        if self.is_running:
            logger.warning("Task detection already running")
            return

        self.is_running = True
        self.stop_event.clear()

        self.detection_thread = threading.Thread(
            target=self._detection_loop,
            daemon=True,
            name="TaskDetector"
        )
        self.detection_thread.start()

        logger.info("Task detection started")

    def stop_detection(self) -> None:
        """Stop task detection."""
        self.is_running = False
        self.stop_event.set()

        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=2.0)

        logger.info("Task detection stopped")

    def _detection_loop(self) -> None:
        """Main detection loop."""
        while not self.stop_event.is_set():
            try:
                # Process queue first
                self._process_queue()

                # Check if enough time has passed since last detection
                if (self.last_detection_time and
                    (datetime.now() - datetime.fromisoformat(self.last_detection_time)).total_seconds() < self.cooldown_period):
                    time.sleep(30)  # Wait longer if in cooldown
                    continue

                # Check for recent activities
                recent_activities = self._get_recent_activities()
                if len(recent_activities) >= 3:  # Need enough context
                    # Detect task accomplishments
                    accomplishments = self._detect_tasks(recent_activities)

                    for accomplishment in accomplishments:
                        if accomplishment.confidence >= self.min_confidence:
                            self._queue_accomplishment(accomplishment)

                time.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error in detection loop: {e}")
                time.sleep(60)

    def _queue_accomplishment(self, accomplishment: TaskAccomplishment) -> None:
        """Add task accomplishment to the queue.

        Args:
            accomplishment: Task accomplishment to queue
        """
        with self.queue_lock:
            # Check if queue is full
            if len(self.detection_queue) >= self.max_queue_size:
                # Remove oldest item
                self.detection_queue.pop(0)
                logger.warning("Detection queue full - removing oldest item")

            # Add to queue
            self.detection_queue.append(accomplishment)
            logger.info(f"Task queued: {accomplishment.task_name} "
                       f"(confidence: {accomplishment.confidence:.2f})")

    def _process_queue(self) -> None:
        """Process the detection queue."""
        current_time = datetime.now()

        with self.queue_lock:
            # Check if we can process items from queue
            if (self.detection_queue and
                (not self.last_detection_time or
                 (current_time - datetime.fromisoformat(self.last_detection_time)).total_seconds() >= self.cooldown_period)):

                # Get the oldest item
                accomplishment = self.detection_queue.pop(0)
                logger.info(f"Processing queued task: {accomplishment.task_name}")

                # Trigger the callback
                self._trigger_accomplishment(accomplishment)

    def get_queue_status(self) -> Dict:
        """Get current queue status.

        Returns:
            Dictionary with queue statistics
        """
        with self.queue_lock:
            return {
                "queue_size": len(self.detection_queue),
                "max_queue_size": self.max_queue_size,
                "is_cooldown_active": (
                    self.last_detection_time and
                    (datetime.now() - datetime.fromisoformat(self.last_detection_time)).total_seconds() < self.cooldown_period
                ),
                "time_until_cooldown_end": (
                    self.cooldown_period - (
                        (datetime.now() - datetime.fromisoformat(self.last_detection_time)).total_seconds()
                        if self.last_detection_time else 0
                    )
                ) if self.last_detection_time else 0,
                "next_in_queue": self.detection_queue[0].task_name if self.detection_queue else None
            }

    def _get_recent_activities(self, minutes: int = 10) -> List[ActivityLogEntry]:
        """Get recent activities for analysis.

        Args:
            minutes: Number of minutes to look back

        Returns:
            List of recent activity log entries
        """
        try:
            # Get activities from the last N minutes
            cutoff_time = datetime.now() - timedelta(minutes=minutes)

            # Load recent logs (in real implementation, this would be more efficient)
            activities = []

            # Try to get activities from log handler
            if hasattr(self.log_handler, 'get_activities'):
                activities = self.log_handler.get_activities(
                    start_time=cutoff_time.isoformat()
                )

            return activities[-20:]  # Return last 20 activities for context

        except Exception as e:
            logger.error(f"Failed to get recent activities: {e}")
            return []

    def _detect_tasks(self, activities: List[ActivityLogEntry]) -> List[TaskAccomplishment]:
        """Use AI to detect task accomplishments from activities.

        Args:
            activities: List of recent activities

        Returns:
            List of detected task accomplishments
        """
        try:
            if len(activities) < 3:
                return []

            # Create prompt for AI analysis
            activities_text = "\n".join([
                f"- {act.timestamp}: {act.window_title} ({act.window_class})"
                for act in activities[-10:]  # Last 10 activities
            ])

            prompt = f"""
Analyze the following recent computer activity to detect task accomplishments:

RECENT ACTIVITIES:
{activities_text}

INSTRUCTIONS:
1. Look for patterns that suggest task completion:
   - Sustained focus on a single task/project
   - Completion-related keywords in titles (e.g., "done", "complete", "finished", "submitted")
   - Abrupt changes in focus indicating task completion
   - Repetitive patterns followed by different activities

2. For each detected task, provide:
   - Task name/description (be specific)
   - Confidence level (0.0 to 1.0)
   - Brief context for why this appears to be a task completion

3. Only report tasks with confidence >= 0.7

Respond in JSON format:
{{
  "detections": [
    {{
      "task_name": "Specific task description",
      "confidence": 0.85,
      "context": "Brief explanation"
    }}
  ]
}}

Focus on genuine task completions, not just activity changes.
"""

            # Use AI to detect tasks
            response = self.ai_service.detect_task_accomplishments(prompt)

            # Parse response to create TaskAccomplishment objects
            if response and "detections" in response:
                return [
                    TaskAccomplishment(
                        task_name=detection["task_name"],
                        confidence=detection["confidence"],
                        timestamp=datetime.now().isoformat(),
                        activity_window=activities,
                        context=detection.get("context", "")
                    )
                    for detection in response["detections"]
                    if detection["confidence"] >= 0.7
                ]

            return []

        except Exception as e:
            logger.error(f"Failed to detect tasks: {e}")
            return []

    def _trigger_accomplishment(self, accomplishment: TaskAccomplishment) -> None:
        """Trigger task accomplishment callback.

        Args:
            accomplishment: Detected task accomplishment
        """
        self.last_detection_time = accomplishment.timestamp

        logger.info(f"Task accomplished: {accomplishment.task_name} "
                   f"(confidence: {accomplishment.confidence:.2f})")

        # Call the callback if set
        if self.detection_callback:
            try:
                self.detection_callback(accomplishment)
            except Exception as e:
                logger.error(f"Error in detection callback: {e}")

    def set_detection_parameters(self, window_size_minutes: int = 10,
                                min_confidence: float = 0.7,
                                cooldown_period: int = 300) -> None:
        """Configure detection parameters.

        Args:
            window_size_minutes: How many minutes of activity to analyze
            min_confidence: Minimum confidence to trigger detection
            cooldown_period: Seconds between detections
        """
        self.window_size_minutes = window_size_minutes
        self.min_confidence = min_confidence
        self.cooldown_period = cooldown_period

        logger.info(f"Detection parameters updated: "
                   f"window={window_size_minutes}min, "
                   f"confidence={min_confidence}, "
                   f"cooldown={cooldown_period}s")

    def set_queue_config(self, max_queue_size: int = 10,
                        queue_check_interval: int = 60) -> None:
        """Configure queue parameters.

        Args:
            max_queue_size: Maximum number of items in queue
            queue_check_interval: Seconds between queue checks
        """
        self.max_queue_size = max_queue_size
        self.queue_check_interval = queue_check_interval

        # Trim queue if new size is smaller
        with self.queue_lock:
            if len(self.detection_queue) > max_queue_size:
                self.detection_queue = self.detection_queue[-max_queue_size:]

        logger.info(f"Queue parameters updated: "
                   f"max_size={max_queue_size}, "
                   f"check_interval={queue_check_interval}s")

    def clear_queue(self) -> int:
        """Clear the detection queue.

        Returns:
            Number of items removed from queue
        """
        with self.queue_lock:
            count = len(self.detection_queue)
            self.detection_queue.clear()
            logger.info(f"Queue cleared - removed {count} items")
            return count

    def process_queue_immediately(self) -> int:
        """Process all items in queue immediately (bypassing cooldown).

        Returns:
            Number of items processed
        """
        processed_count = 0

        while True:
            with self.queue_lock:
                if not self.detection_queue:
                    break

                # Get next item
                accomplishment = self.detection_queue.pop(0)
                processed_count += 1

            # Process item (outside lock)
            self._trigger_accomplishment(accomplishment)

        logger.info(f"Processed {processed_count} items from queue")
        return processed_count

    def get_detection_stats(self) -> Dict:
        """Get statistics about task detection.

        Returns:
            Dictionary with detection statistics
        """
        return {
            "is_running": self.is_running,
            "last_detection": self.last_detection_time,
            "window_size_minutes": self.window_size_minutes,
            "min_confidence": self.min_confidence,
            "cooldown_period": self.cooldown_period,
            "detections_count": getattr(self, 'detections_count', 0)
        }

    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop_detection()
        self.detection_callback = None


# Global instance for the application
_task_detection_service: Optional[TaskDetectionService] = None


def get_task_detection_service() -> TaskDetectionService:
    """Get or create the global task detection service."""
    global _task_detection_service

    if _task_detection_service is None:
        _task_detection_service = TaskDetectionService()

    return _task_detection_service


def initialize_task_detection() -> TaskDetectionService:
    """Initialize and start the task detection service."""
    service = get_task_detection_service()
    service.start_detection()
    return service


def shutdown_task_detection() -> None:
    """Shut down the task detection service."""
    global _task_detection_service

    if _task_detection_service is not None:
        _task_detection_service.cleanup()
        _task_detection_service = None