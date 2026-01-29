"""Integration tests for tracking flow.

Tests that:
- Tracker can be started
- Window switches are logged
- Log file updates correctly
- Background thread runs properly
"""

import pytest
import time
import json
from pathlib import Path
from unittest.mock import patch, Mock
from datetime import datetime

from services.tracker import TrackerService
from utils.file_handler import read_json


class TestTrackingFlow:
    """Integration tests for complete tracking workflow."""

    @pytest.fixture
    def temp_log_path(self, tmp_path):
        """Provide temporary log file path."""
        return tmp_path / "logs.json"

    @pytest.fixture
    def mock_window_titles(self):
        """Provide sequence of mock window titles."""
        return [
            "Visual Studio Code - Google Chrome",
            "GitHub - python/requests - Google Chrome",
            "Stack Overflow - Mozilla Firefox",
            "PyCharm - Microsoft Edge",
        ]

    def test_tracker_start_creates_log_file(self, temp_log_path):
        """Test that starting tracker creates logs.json file."""
        with patch("services.tracker.LOGS_FILE", temp_log_path):
            service = TrackerService()
            service.start_tracking()

            # Wait briefly for thread to start
            time.sleep(0.5)

            # Stop tracker
            service.stop_tracking()

            # Verify log file was created
            assert temp_log_path.exists()

    def test_window_switches_are_logged(self, temp_log_path, mock_window_titles):
        """Test that window switches are captured and logged."""
        with patch("services.tracker.LOGS_FILE", temp_log_path), patch(
            "services.tracker.win32gui"
        ) as mock_win32gui:
            # Setup mock to return different titles
            mock_win32gui.GetForegroundWindow.return_value = 12345
            mock_win32gui.GetWindowText.side_effect = mock_window_titles

            service = TrackerService()
            service.start_tracking()

            # Let tracker capture a few windows
            time.sleep(1)

            service.stop_tracking()

            # Read log file
            data = read_json(temp_log_path)
            assert data is not None
            assert "entries" in data

            # Verify entries were captured (browser suffixes removed)
            entries = data["entries"]
            assert len(entries) > 0

            # Check that browser suffixes were filtered
            first_entry = entries[0]
            assert "Google Chrome" not in first_entry["window_title"]

    def test_background_thread_polling(self, temp_log_path):
        """Test that tracker runs in background thread."""
        with patch("services.tracker.LOGS_FILE", temp_log_path), patch(
            "services.tracker.win32gui"
        ) as mock_win32gui:
            mock_win32gui.GetForegroundWindow.return_value = 12345
            mock_win32gui.GetWindowText.return_value = "Test Window"

            service = TrackerService()
            service.start_tracking()

            # Verify thread is running
            assert service.is_tracking() is True

            # Let it run briefly
            time.sleep(0.5)

            # Stop and verify
            service.stop_tracking()
            assert service.is_tracking() is False

    def test_tracker_handles_windows_exceptions(self, temp_log_path):
        """Test that tracker gracefully handles Windows exceptions."""
        with patch("services.tracker.LOGS_FILE", temp_log_path), patch(
            "services.tracker.win32gui"
        ) as mock_win32gui:
            # Simulate Windows error
            mock_win32gui.GetForegroundWindow.side_effect = Exception("Windows error")

            service = TrackerService()
            service.start_tracking()

            # Should not crash
            time.sleep(0.5)

            service.stop_tracking()

            # Tracker should still be stoppable
            assert service.is_tracking() is False

    def test_tracker_respects_polling_interval(self, temp_log_path):
        """Test that tracker respects the 5-second polling interval."""
        with patch("services.tracker.LOGS_FILE", temp_log_path), patch(
            "services.tracker.win32gui"
        ) as mock_win32gui:
            mock_win32gui.GetForegroundWindow.return_value = 12345
            mock_win32gui.GetWindowText.return_value = "Test Window"

            service = TrackerService()
            service.start_tracking()

            # Count calls in 2 seconds (should be 0-1 given 5s interval)
            initial_count = mock_win32gui.GetWindowText.call_count
            time.sleep(2)

            final_count = mock_win32gui.GetWindowText.call_count

            # Should not have polled many times (interval is 5s)
            # Allow some tolerance for thread startup
            assert final_count - initial_count <= 2

            service.stop_tracking()

    def test_empty_window_titles_are_not_logged(self, temp_log_path):
        """Test that empty window titles are not logged."""
        with patch("services.tracker.LOGS_FILE", temp_log_path), patch(
            "services.tracker.win32gui"
        ) as mock_win32gui:
            # Return empty title
            mock_win32gui.GetForegroundWindow.return_value = 12345
            mock_win32gui.GetWindowText.return_value = ""

            service = TrackerService()
            service.start_tracking()

            time.sleep(0.5)

            service.stop_tracking()

            # Read log file
            data = read_json(temp_log_path)

            # Empty titles should not create entries (or be filtered out)
            if data and data.get("entries"):
                # If entries exist, none should have empty window_title
                assert all(entry["window_title"] != "" for entry in data["entries"])

    def test_log_file_metadata_updated(self, temp_log_path):
        """Test that log file metadata is updated correctly."""
        with patch("services.tracker.LOGS_FILE", temp_log_path), patch(
            "services.tracker.win32gui"
        ) as mock_win32gui:
            mock_win32gui.GetForegroundWindow.return_value = 12345
            mock_win32gui.GetWindowText.return_value = "Test Window"

            service = TrackerService()
            service.start_tracking()

            time.sleep(0.5)

            service.stop_tracking()

            # Read and verify metadata
            data = read_json(temp_log_path)
            assert data is not None
            assert "metadata" in data
            assert "version" in data["metadata"]
            assert "total_entries" in data["metadata"]
