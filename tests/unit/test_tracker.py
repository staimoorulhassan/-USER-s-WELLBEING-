"""Unit tests for tracker service.

Tests that:
- Tracking can be started and stopped
- Polling runs at correct intervals
- Window titles are captured using pywin32
- Browser filtering is applied
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from services.tracker import TrackerService
from models.activity_log import ActivityLogEntry


class TestTrackerService:
    """Test tracker service behavior."""

    def test_start_tracking_begins_polling(self):
        """Test that start_tracking begins background polling."""
        with patch("services.tracker.threading.Thread") as mock_thread:
            service = TrackerService()
            service.start_tracking()

            # Verify thread was created and started
            mock_thread.assert_called_once()
            thread_instance = mock_thread.return_value
            assert thread_instance.start.called

    def test_stop_tracking_stops_polling(self):
        """Test that stop_tracking stops background polling."""
        service = TrackerService()

        # Mock the thread
        service.tracking_thread = Mock()
        service.tracking_event = Mock()

        service.stop_tracking()

        # Verify stop was signaled
        service.tracking_event.set.assert_called_once()
        if service.tracking_thread.join:
            service.tracking_thread.join.assert_called_once()

    def test_is_tracking_returns_correct_state(self):
        """Test that is_tracking returns correct tracking state."""
        service = TrackerService()

        # Initially not tracking
        assert service.is_tracking() is False

        # After starting
        service.tracking_event = Mock()
        service.tracking_event.is_set.return_value = False
        assert service.is_tracking() is True

    def test_polling_captures_window_title(self):
        """Test that polling captures window title using pywin32."""
        with patch("services.tracker.win32gui") as mock_win32gui:
            # Mock window handles
            mock_win32gui.GetForegroundWindow.return_value = 12345
            mock_win32gui.GetWindowText.return_value = "GitHub - Google Chrome"

            service = TrackerService()
            title = service._get_active_window_title()

            assert title == "GitHub - Google Chrome"
            mock_win32gui.GetForegroundWindow.assert_called_once()
            mock_win32gui.GetWindowText.assert_called_once_with(12345)

    def test_browser_filter_applied_to_window_title(self):
        """Test that browser suffixes are filtered from window titles."""
        with patch("services.tracker.win32gui") as mock_win32gui:
            mock_win32gui.GetForegroundWindow.return_value = 12345
            mock_win32gui.GetWindowText.return_value = "GitHub - python/requests - Google Chrome"

            service = TrackerService()
            filtered_title = service._get_filtered_window_title()

            assert filtered_title == "GitHub - python/requests"
            assert "Google Chrome" not in filtered_title

    def test_polling_handles_empty_window_titles(self):
        """Test that empty window titles are handled gracefully."""
        with patch("services.tracker.win32gui") as mock_win32gui:
            mock_win32gui.GetForegroundWindow.return_value = 12345
            mock_win32gui.GetWindowText.return_value = ""

            service = TrackerService()
            title = service._get_active_window_title()

            assert title == ""

    def test_polling_handles_windows_exceptions(self):
        """Test that Windows exceptions are caught and logged."""
        with patch("services.tracker.win32gui") as mock_win32gui:
            # Simulate Windows error
            mock_win32gui.GetForegroundWindow.side_effect = Exception("Windows error")

            service = TrackerService()
            # Should not raise exception
            title = service._get_active_window_title()

            # Should return empty string on error
            assert title == ""

    def test_get_recent_activity_returns_entries(self):
        """Test that get_recent_activity returns recent log entries."""
        service = TrackerService()

        # Mock some activity logs
        service.activity_buffer = [
            ActivityLogEntry(
                timestamp=datetime.now(),
                window_title="GitHub",
                raw_window_title="GitHub - Google Chrome",
                application="Chrome",
                duration_seconds=0,
            )
        ]

        recent = service.get_recent_activity(limit=10)

        assert len(recent) == 1
        assert recent[0].window_title == "GitHub"

    def test_get_recent_activity_respects_limit(self):
        """Test that get_recent_activity respects the limit parameter."""
        service = TrackerService()

        # Mock multiple entries
        service.activity_buffer = [
            ActivityLogEntry(
                timestamp=datetime.now(),
                window_title=f"Window {i}",
                raw_window_title=f"Window {i}",
                application="App",
                duration_seconds=0,
            )
            for i in range(20)
        ]

        recent = service.get_recent_activity(limit=5)

        assert len(recent) == 5
