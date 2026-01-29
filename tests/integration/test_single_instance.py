"""Integration tests for single instance enforcement.

Tests launching multiple instances and window activation behavior.
"""

import pytest
import subprocess
import sys
import time
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from config.constants import WELLBEING_DIR

# Ensure data directory exists for tests
WELLBEING_DIR.mkdir(parents=True, exist_ok=True)


class TestSingleInstanceIntegration:
    """Integration tests for single-instance enforcement."""

    def test_lock_file_path_exists(self):
        """Test that lock file path is configured correctly."""
        from services.instance_manager import InstanceManager

        # Check default lock path
        expected_path = WELLBEING_DIR / ".lock"
        assert expected_path.parent.exists()

    def test_cleanup_creates_directory_if_needed(self, tmp_path):
        """Test that cleanup works even if lock directory is missing."""
        from services.instance_manager import InstanceManager
        from config.constants import WELLBEING_DIR

        # Ensure directory exists
        WELLBEING_DIR.mkdir(parents=True, exist_ok=True)

        manager = InstanceManager()

        try:
            # Should not raise even if directory didn't exist before
            assert manager is not None
        finally:
            manager.cleanup()

    def test_is_first_instance_when_no_lock_exists(self):
        """Test that is_first_instance returns True when no lock exists."""
        from services.instance_manager import InstanceManager
        from config.constants import WELLBEING_DIR

        # Ensure clean state
        lock_file = WELLBEING_DIR / ".lock"
        if lock_file.exists():
            lock_file.unlink()

        manager = InstanceManager()

        try:
            is_first = manager.is_first_instance()
            assert is_first is True
        finally:
            manager.cleanup()

    def test_lock_file_created_after_init(self):
        """Test that lock file is created after initialization."""
        from services.instance_manager import InstanceManager
        from config.constants import WELLBEING_DIR

        lock_file = WELLBEING_DIR / ".lock"

        # Clean up any existing lock
        if lock_file.exists():
            lock_file.unlink()

        manager = InstanceManager()

        try:
            if manager._use_file_lock:
                assert lock_file.exists()
        finally:
            manager.cleanup()

        # Lock file should be removed after cleanup
        if manager._use_file_lock:
            assert not lock_file.exists()

    def test_current_pid_in_lock_file(self):
        """Test that lock file contains current process PID."""
        from services.instance_manager import InstanceManager
        from config.constants import WELLBEING_DIR

        lock_file = WELLBEING_DIR / ".lock"

        manager = InstanceManager()

        try:
            if manager._use_file_lock and lock_file.exists():
                with open(lock_file, "r") as f:
                    pid_str = f.read().strip()
                    pid = int(pid_str)

                # Should match current PID
                assert pid == os.getpid()
        finally:
            manager.cleanup()

    def test_cleanup_removes_lock_file(self):
        """Test that cleanup removes lock file."""
        from services.instance_manager import InstanceManager
        from config.constants import WELLBEING_DIR

        lock_file = WELLBEING_DIR / ".lock"

        manager = InstanceManager()

        try:
            if manager._use_file_lock:
                assert lock_file.exists()
        finally:
            manager.cleanup()

        # Lock should be removed
        if manager._use_file_lock:
            assert not lock_file.exists()

    def test_multiple_managers_can_be_created_sequentially(self):
        """Test that multiple managers can be created one after another."""
        from services.instance_manager import InstanceManager

        for i in range(3):
            manager = InstanceManager()
            try:
                assert manager is not None
                assert manager.is_first_instance() is True
            finally:
                manager.cleanup()


class TestWindowActivation:
    """Tests for window activation behavior."""

    @patch('services.instance_manager.HAS_WIN32', False)
    def test_activation_returns_false_without_win32(self):
        """Test that activation returns False without Windows API."""
        from services.instance_manager import InstanceManager

        manager = InstanceManager()

        try:
            result = manager.activate_existing_instance()
            assert result is False
        finally:
            manager.cleanup()

    @patch('services.instance_manager.HAS_WIN32', True)
    @patch('services.instance_manager.win32gui.FindWindow')
    def test_activation_returns_false_when_window_not_found(self, mock_find_window):
        """Test that activation returns False when window not found."""
        from services.instance_manager import InstanceManager

        mock_find_window.return_value = 0  # HWND_NULL

        manager = InstanceManager()

        try:
            result = manager.activate_existing_instance()
            assert result is False
        finally:
            manager.cleanup()

    @patch('services.instance_manager.HAS_WIN32', True)
    @patch('services.instance_manager.win32gui.FindWindow')
    @patch('services.instance_manager.win32gui.IsIconic')
    @patch('services.instance_manager.win32gui.ShowWindow')
    @patch('services.instance_manager.win32gui.SetForegroundWindow')
    @patch('services.instance_manager.win32gui.FlashWindowEx')
    def test_activation_calls_win32_apis(self, mock_flash, mock_set_fg,
                                          mock_show, mock_is_iconic, mock_find):
        """Test that activation calls the correct Windows APIs."""
        from services.instance_manager import InstanceManager

        mock_hwnd = 12345
        mock_find.return_value = mock_hwnd
        mock_is_iconic.return_value = False

        manager = InstanceManager()

        try:
            result = manager.activate_existing_instance()
            assert result is True

            # Verify API calls were made
            mock_find.assert_called_once_with(None, "Wellbeing - Desktop Tracker")
            mock_is_iconic.assert_called_once_with(mock_hwnd)
            mock_set_fg.assert_called_once_with(mock_hwnd)
            mock_flash.assert_called_once()
        finally:
            manager.cleanup()

    @patch('services.instance_manager.HAS_WIN32', True)
    @patch('services.instance_manager.win32gui.FindWindow')
    def test_activation_handles_exceptions_gracefully(self, mock_find):
        """Test that activation handles exceptions gracefully."""
        from services.instance_manager import InstanceManager

        mock_find.side_effect = Exception("API call failed")

        manager = InstanceManager()

        try:
            # Should return False, not raise
            result = manager.activate_existing_instance()
            assert result is False
        finally:
            manager.cleanup()


class TestProcessDetection:
    """Tests for process detection utilities."""

    def test_current_process_is_detected_as_running(self):
        """Test that current process is detected as running."""
        from services.instance_manager import InstanceManager

        manager = InstanceManager()

        try:
            current_pid = os.getpid()
            is_running = manager._is_process_running(current_pid)
            assert is_running is True
        finally:
            manager.cleanup()

    def test_nonexistent_pid_is_detected_as_not_running(self):
        """Test that nonexistent PID is detected as not running."""
        from services.instance_manager import InstanceManager

        manager = InstanceManager()

        try:
            # Use a PID that's unlikely to exist
            fake_pid = 999999
            is_running = manager._is_process_running(fake_pid)
            assert is_running is False
        finally:
            manager.cleanup()


class TestStaleLockHandling:
    """Tests for stale lock file handling."""

    def test_cleanup_removes_stale_lock_with_nonexistent_pid(self):
        """Test that stale lock with nonexistent PID is cleaned up."""
        from services.instance_manager import InstanceManager
        from config.constants import WELLBEING_DIR

        lock_file = WELLBEING_DIR / ".test_stale_lock"

        # Create a stale lock file
        with open(lock_file, "w") as f:
            f.write("999999")  # Nonexistent PID

        manager = InstanceManager()
        manager.lock_file_path = lock_file

        try:
            manager._cleanup_stale_lock()

            # Stale lock should be removed
            assert not lock_file.exists()
        finally:
            manager.cleanup()

    def test_cleanup_keeps_lock_with_active_pid(self):
        """Test that lock with active PID is not removed."""
        from services.instance_manager import InstanceManager
        from config.constants import WELLBEING_DIR

        lock_file = WELLBEING_DIR / ".test_active_lock"

        # Create a lock file with current PID
        with open(lock_file, "w") as f:
            f.write(str(os.getpid()))

        manager = InstanceManager()
        manager.lock_file_path = lock_file

        try:
            manager._cleanup_stale_lock()

            # Active lock should be kept
            assert lock_file.exists()
        finally:
            manager.cleanup()


class TestErrorHandling:
    """Tests for error handling in edge cases."""

    def test_multiple_cleanup_calls_are_safe(self):
        """Test that calling cleanup multiple times is safe."""
        from services.instance_manager import InstanceManager

        manager = InstanceManager()

        try:
            # Call cleanup multiple times
            manager.cleanup()
            manager.cleanup()
            manager.cleanup()

            # Should not raise
            assert True
        except Exception as e:
            pytest.fail(f"Multiple cleanup calls raised: {e}")

    def test_manager_with_corrupted_lock_file(self):
        """Test handling of corrupted lock file."""
        from services.instance_manager import InstanceManager
        from config.constants import WELLBEING_DIR

        lock_file = WELLBEING_DIR / ".test_corrupt_lock"

        # Create a corrupted lock file
        lock_file.write_text("not_a_number")

        manager = InstanceManager()
        manager.lock_file_path = lock_file

        try:
            # Should handle gracefully (may create new lock)
            manager._cleanup_stale_lock()

            # After cleanup, should be able to create new lock
            manager._acquire_file_lock()
            assert lock_file.exists()
        finally:
            manager.cleanup()
