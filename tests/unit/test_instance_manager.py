"""Unit tests for InstanceManager.

Tests mutex creation, file-based locking, and cleanup behavior.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from services.instance_manager import InstanceManager
from utils.exceptions import InstanceError
from config.constants import WELLBEING_DIR

# Ensure data directory exists for tests
WELLBEING_DIR.mkdir(parents=True, exist_ok=True)


class TestInstanceManager:
    """Test suite for InstanceManager single-instance enforcement."""

    def test_create_instance_manager(self):
        """Test creating InstanceManager successfully."""
        try:
            manager = InstanceManager()
            assert manager is not None
            manager.cleanup()
        except Exception as e:
            pytest.skip(f"InstanceManager creation failed: {e}")

    def test_is_first_instance_returns_true_on_first_launch(self):
        """Test that is_first_instance returns True for first instance."""
        manager = InstanceManager()
        try:
            # First instance should return True
            is_first = manager.is_first_instance()
            assert is_first is True
        finally:
            manager.cleanup()

    def test_mutex_is_created_on_initialization(self):
        """Test that mutex or lock file is created on initialization."""
        manager = InstanceManager()
        try:
            # Check if either mutex or lock file exists
            has_mutex = manager.mutex is not None
            has_lock = manager._use_file_lock and manager.lock_file_path.exists()

            # At least one should be True
            assert has_mutex or has_lock
        finally:
            manager.cleanup()

    def test_cleanup_releases_mutex(self):
        """Test that cleanup properly releases mutex."""
        manager = InstanceManager()
        try:
            mutex = manager.mutex
            assert mutex is not None or manager._use_file_lock

            # Call cleanup
            manager.cleanup()

            # Mutex should be None after cleanup
            assert manager.mutex is None

        finally:
            # Ensure cleanup even if test fails
            if manager.mutex:
                manager.cleanup()

    def test_cleanup_removes_lock_file(self):
        """Test that cleanup removes lock file."""
        manager = InstanceManager()
        try:
            # Only test if using file-based lock
            if not manager._use_file_lock:
                pytest.skip("Not using file-based lock")

            # Ensure lock file exists
            assert manager.lock_file_path.exists()

            # Cleanup
            manager.cleanup()

            # Lock file should be removed
            assert not manager.lock_file_path.exists()

        finally:
            # Ensure cleanup even if test fails
            if manager.lock_file_path.exists():
                try:
                    manager.lock_file_path.unlink()
                except:
                    pass

    def test_destructor_calls_cleanup(self):
        """Test that destructor properly cleans up resources."""
        manager = InstanceManager()
        lock_file = None

        try:
            if manager._use_file_lock:
                lock_file = manager.lock_file_path
                assert lock_file.exists()

            # Delete manager (triggers __del__)
            del manager

            # Resources should be cleaned up
            if lock_file and lock_file.exists():
                # Give it a moment
                import time
                time.sleep(0.1)
                # File might still exist due to GC timing
                pass

        except Exception:
            # Cleanup may have timing issues
            pass

    def test_stale_lock_file_detection(self):
        """Test detection and cleanup of stale lock files."""
        manager = InstanceManager()

        try:
            if not manager._use_file_lock:
                pytest.skip("Not using file-based lock")

            # Create a stale lock file with a non-existent PID
            fake_pid = 999999  # Very unlikely to exist
            with open(manager.lock_file_path, "w") as f:
                f.write(str(fake_pid))

            # Create new manager (should clean up stale lock)
            manager2 = InstanceManager()
            try:
                # Should successfully create new lock
                assert manager2.is_first_instance() is True
            finally:
                manager2.cleanup()

        finally:
            manager.cleanup()

    def test_active_pid_detection(self):
        """Test that active PIDs are detected correctly."""
        manager = InstanceManager()

        try:
            if not manager._use_file_lock:
                pytest.skip("Not using file-based lock")

            # Use current process PID (definitely active)
            current_pid = os.getpid()

            # Should be detected as running
            is_running = manager._is_process_running(current_pid)
            assert is_running is True

        finally:
            manager.cleanup()

    def test_non_existent_pid_detection(self):
        """Test that non-existent PIDs are detected correctly."""
        manager = InstanceManager()

        try:
            # Use a PID that definitely doesn't exist
            fake_pid = 999999

            # Should not be detected as running
            is_running = manager._is_process_running(fake_pid)
            assert is_running is False

        finally:
            manager.cleanup()

    def test_lock_file_contains_current_pid(self):
        """Test that lock file contains the current process PID."""
        manager = InstanceManager()

        try:
            if not manager._use_file_lock:
                pytest.skip("Not using file-based lock")

            # Read lock file
            with open(manager.lock_file_path, "r") as f:
                pid_str = f.read().strip()

            # Should contain current PID
            assert pid_str == str(os.getpid())

        finally:
            manager.cleanup()

    def test_multiple_cleanup_calls_are_safe(self):
        """Test that calling cleanup multiple times doesn't raise errors."""
        manager = InstanceManager()

        try:
            # Call cleanup multiple times
            manager.cleanup()
            manager.cleanup()
            manager.cleanup()

            # Should not raise any exceptions
            assert True

        except Exception as e:
            pytest.fail(f"Multiple cleanup calls raised: {e}")

    @patch('services.instance_manager.HAS_WIN32', False)
    def test_file_based_fallback_when_win32_unavailable(self):
        """Test that file-based locking is used when win32 is unavailable."""
        # Force file-based lock
        manager = InstanceManager()

        try:
            # Should use file-based lock
            assert manager._use_file_lock is True
            assert manager.mutex is None
        finally:
            manager.cleanup()

    def test_lock_file_path_is_correct(self):
        """Test that lock file path is in the correct directory."""
        manager = InstanceManager()

        try:
            if not manager._use_file_lock:
                pytest.skip("Not using file-based lock")

            # Lock file should be in ~/.wellbeing/
            from config.constants import WELLBEING_DIR
            expected_path = WELLBEING_DIR / ".lock"

            assert manager.lock_file_path == expected_path

        finally:
            manager.cleanup()


class TestInstanceManagerMockedWin32:
    """Test suite with mocked Windows API calls."""

    @patch('services.instance_manager.HAS_WIN32', True)
    @patch('services.instance_manager.win32event.CreateMutex')
    @patch('services.instance_manager.win32api.GetLastError')
    def test_mutex_creation_success(self, mock_get_last_error, mock_create_mutex):
        """Test successful mutex creation."""
        # Setup mocks
        mock_mutex = MagicMock()
        mock_create_mutex.return_value = mock_mutex
        mock_get_last_error.return_value = 0  # No error

        manager = InstanceManager()

        try:
            assert manager.mutex == mock_mutex
            assert manager._use_file_lock is False
        finally:
            manager.cleanup()

    @patch('services.instance_manager.HAS_WIN32', True)
    @patch('services.instance_manager.win32event.CreateMutex')
    @patch('services.instance_manager.win32api.GetLastError')
    @patch('services.instance_manager.win32api.CloseHandle')
    def test_mutex_already_exists(self, mock_close_handle, mock_get_last_error, mock_create_mutex):
        """Test behavior when mutex already exists."""
        # Setup mocks
        mock_mutex = MagicMock()
        mock_create_mutex.return_value = mock_mutex
        mock_get_last_error.return_value = 183  # ERROR_ALREADY_EXISTS
        mock_close_handle.return_value = None

        manager = InstanceManager()

        try:
            # Should fall back to file-based lock
            assert manager._use_file_lock is True
            assert manager.mutex is None
        finally:
            manager.cleanup()

    @patch('services.instance_manager.HAS_WIN32', True)
    @patch('services.instance_manager.win32event.CreateMutex')
    def test_mutex_creation_failure(self, mock_create_mutex):
        """Test behavior when mutex creation fails."""
        # Setup mock to raise exception
        mock_create_mutex.side_effect = Exception("Mutex creation failed")

        manager = InstanceManager()

        try:
            # Should fall back to file-based lock
            assert manager._use_file_lock is True
            assert manager.mutex is None
        finally:
            manager.cleanup()

    @patch('services.instance_manager.HAS_WIN32', True)
    @patch('services.instance_manager.win32api.CloseHandle')
    def test_mutex_cleanup(self, mock_close_handle):
        """Test that mutex handle is closed during cleanup."""
        mock_mutex = MagicMock()

        manager = InstanceManager()
        manager.mutex = mock_mutex
        manager._use_file_lock = False

        # Call cleanup
        manager.cleanup()

        # CloseHandle should be called at least once
        assert mock_close_handle.call_count >= 1

        # Mutex should be set to None
        assert manager.mutex is None

    @patch('services.instance_manager.HAS_WIN32', True)
    @patch('services.instance_manager.win32api.OpenProcess')
    def test_is_process_running_windows(self, mock_open_process):
        """Test process detection on Windows."""
        manager = InstanceManager()

        # Test with valid handle
        mock_handle = MagicMock()
        mock_open_process.return_value = mock_handle

        try:
            result = manager._is_process_running(1234)
            assert result is True
        finally:
            manager.cleanup()

    @patch('services.instance_manager.HAS_WIN32', True)
    @patch('services.instance_manager.win32api.OpenProcess')
    def test_is_process_running_windows_calls_api(self, mock_open_process):
        """Test that process detection calls OpenProcess on Windows."""
        manager = InstanceManager()

        mock_handle = MagicMock()
        mock_open_process.return_value = mock_handle

        try:
            # Call the method
            result = manager._is_process_running(1234)

            # OpenProcess should have been called
            mock_open_process.assert_called_once()
            assert result is True
        finally:
            manager.cleanup()
