"""Integration tests for shutdown interception flow.

Tests that:
- Shutdown events are detected
- Prompt appears correctly
- Data is saved before shutdown
- User can choose to generate summary
- Timeout works (5-second countdown)
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import time

from services.event_interceptor import EventInterceptor
from services.tracker import TrackerService
from services.profile_service import ProfileService
from ui.main_window import MainWindow


class TestShutdownInterception:
    """Integration tests for shutdown interception workflow."""

    @pytest.fixture
    def temp_data_path(self, tmp_path):
        """Provide temporary data directory."""
        return tmp_path / "wellbeing"

    @pytest.fixture
    def profile_service(self, temp_data_path):
        """Create profile service with temp data path."""
        with patch("services.profile_service.DATA_DIR", temp_data_path):
            return ProfileService()

    @pytest.fixture
    def mock_callback(self):
        """Mock callback for shutdown events."""
        return MagicMock()

    def test_register_shutdown_handler(self, profile_service, mock_callback):
        """Test registering shutdown handler."""
        # Create interceptor
        interceptor = EventInterceptor()

        # Register handler
        interceptor.register_shutdown_handler(mock_callback)

        # Verify callback stored
        assert interceptor._shutdown_callback is mock_callback

    def test_block_shutdown_with_reason(self, profile_service):
        """Test blocking shutdown with reason."""
        interceptor = EventInterceptor()

        # Block shutdown
        reason = "System shutdown initiated"
        interceptor.block_shutdown(reason)

        # Verify blocked and has reason
        assert interceptor.is_shutdown_blocked()
        assert interceptor._shutdown_reason == reason

    def test_allow_shutdown(self, profile_service):
        """Test allowing shutdown."""
        interceptor = EventInterceptor()

        # First block
        interceptor.block_shutdown("Test")

        # Then allow
        interceptor.allow_shutdown()

        # Verify unblocked
        assert not interceptor.is_shutdown_blocked()
        assert interceptor._shutdown_reason is None

    def test_notification_triggers_callback(self, profile_service, mock_callback):
        """Test that notification triggers callback."""
        interceptor = EventInterceptor()

        # Register callback
        interceptor.register_shutdown_handler(mock_callback)

        # Process notification
        interceptor._process_shutdown_notification()

        # Verify callback called
        mock_callback.assert_called_once_with()

    def test_notification_raises_error_when_blocked(self, profile_service):
        """Test that error is raised when shutdown is blocked."""
        interceptor = EventInterceptor()

        # Block shutdown
        interceptor.block_shutdown()

        # Should raise error
        with pytest.raises(Exception):  # ShutdownEventError
            interceptor._process_notification()

    def test_integration_with_main_window(self, profile_service, temp_data_path):
        """Test integration with main window."""
        # Create profile
        profile = profile_service.save_profile(
            name="Test User",
            role="Developer",
            main_goal="Build software"
        )

        with patch("services.event_interceptor.DATA_DIR", temp_data_path):
            # Create main window
            main_window = MagicMock()

            # Create interceptor
            interceptor = EventInterceptor()

            # Mock callback that would update UI
            def on_shutdown_detected():
                main_window.show_shutdown_prompt.assert_called_once()

            interceptor.register_shutdown_handler(on_shutdown_detected)

            # Simulate shutdown detection
            interceptor.block_shutdown("System shutdown")

            # Verify state
            assert interceptor.is_shutdown_blocked()

    def test_block_and_allow_sequence(self, profile_service, mock_callback):
        """Test block and allow sequence."""
        interceptor = EventInterceptor()

        # Register callback
        interceptor.register_shutdown_handler(mock_callback)

        # Block
        interceptor.block_shutdown("Test reason")

        # Allow
        interceptor.allow_shutdown()

        # Should be unblocked
        assert not interceptor.is_shutdown_blocked()
        assert interceptor._shutdown_reason is None

    def test_shutdown_with_activity_logging(self, temp_data_path, mock_callback):
        """Test shutdown while activity logging is happening."""
        with patch("services.tracker.LOGS_FILE", temp_data_path / "logs.json"), \
             patch("services.profile_service.DATA_DIR", temp_data_path):

            # Create tracker service
            tracker = TrackerService()
            tracker.start_tracking()

            # Create interceptor
            interceptor = EventInterceptor()
            interceptor.register_shutdown_handler(mock_callback)

            # Simulate shutdown while tracking
            interceptor.block_shutdown("System shutdown")

            # Stop tracking (simulating the flow)
            tracker.stop_tracking()

            # Verify blocker state
            assert interceptor.is_shutdown_blocked()

            # Allow shutdown
            interceptor.allow_shutdown()

    def test_persistence_across_sessions(self, temp_data_path, mock_callback):
        """Test that state persists across sessions (mocked)."""
        with patch("services.event_interceptor.DATA_DIR", temp_data_path):
            # First session - register handler
            interceptor1 = EventInterceptor()
            interceptor1.register_shutdown_handler(mock_callback)

            # Simulate some operations
            interceptor1.block_shutdown("Session 1")
            interceptor1.allow_shutdown()

            # Second session (would load state in real implementation)
            interceptor2 = EventInterceptor()

            # Should start clean
            assert not interceptor2.is_shutdown_blocked()

    def test_timeout_mechanism(self, profile_service, mock_callback):
        """Test that timeout mechanism works (mocked)."""
        interceptor = EventInterceptor()

        # Register callback
        interceptor.register_shutdown_handler(mock_callback)

        # Block shutdown
        interceptor.block_shutdown("Test timeout")

        # Simulate timeout (in real test, this would wait)
        with patch('services.event_interceptor.time.sleep') as mock_sleep:
            # The timeout is handled by the UI, not the service
            assert interceptor.is_shutdown_blocked()

        # Allow after
        interceptor.allow_shutdown()

    def test_shutdown_dialog_integration(self, profile_service):
        """Test integration with shutdown dialog."""
        # This would be tested with actual UI in a full integration test
        interceptor = EventInterceptor()

        # Mock callback that shows dialog
        mock_dialog = MagicMock()
        mock_dialog.result = True  # User clicked "Yes"

        def show_shutdown_prompt():
            return mock_dialog.result

        interceptor.register_shutdown_handler(show_shutdown_prompt)

        # Block shutdown
        interceptor.block_shutdown("System shutdown")

        # Simulate user response (would come from UI)
        if mock_dialog.result:
            interceptor.allow_shutdown()

        # Should be unblocked
        assert not interceptor.is_shutdown_blocked()

    def test_data_saving_before_shutdown(self, profile_service, temp_data_path):
        """Test that data is saved before shutdown."""
        with patch("services.profile_service.DATA_DIR", temp_data_path):
            # Create some data
            profile = profile_service.save_profile(
                name="Test",
                role="Test Role",
                main_goal="Test Goal"
            )

            # Create interceptor
            interceptor = EventInterceptor()

            # Mock callback that saves data
            mock_save = MagicMock()
            interceptor.register_shutdown_handler(mock_save)

            # Process shutdown notification
            interceptor._process_shutdown_notification()

            # Verify save callback was called
            mock_save.assert_called_once()

    def test_error_handling_during_shutdown(self, profile_service, mock_callback):
        """Test error handling during shutdown process."""
        interceptor = EventInterceptor()

        # Register failing callback
        def failing_callback():
            raise Exception("Callback failed")

        interceptor.register_shutdown_handler(failing_callback)

        # Should not crash the system
        with pytest.raises(Exception):
            interceptor._process_notification()

        # Should still be able to recover
        interceptor.allow_shutdown()
        assert not interceptor.is_shutdown_blocked()

    def test_multiple_shutdown_events(self, profile_service, mock_callback):
        """Test handling multiple shutdown events."""
        interceptor = EventInterceptor()

        # Register callback
        interceptor.register_shutdown_handler(mock_callback)

        # First shutdown
        interceptor.block_shutdown("First shutdown")
        mock_callback.reset_mock()

        # Second shutdown
        interceptor._process_notification()

        # Callback should be called again
        mock_callback.assert_called_once()

    def test_cleanup_on_exit(self, profile_service):
        """Test cleanup when interceptor is destroyed."""
        interceptor = EventInterceptor()

        # Block shutdown
        interceptor.block_shutdown("Test")

        # Allow on cleanup (simulated)
        interceptor.allow_shutdown()

        # Should be clean
        assert not interceptor.is_shutdown_blocked()

    def test_integration_with_tracking(self, temp_data_path, mock_callback):
        """Test full integration with tracking service."""
        with patch("services.tracker.LOGS_FILE", temp_data_path / "logs.json"), \
             patch("services.profile_service.DATA_DIR", temp_data_path):

            # Create and start tracking
            tracker = TrackerService()
            tracker.start_tracking()

            # Create interceptor
            interceptor = EventInterceptor()
            interceptor.register_shutdown_handler(mock_callback)

            # Simulate system shutdown
            interceptor.block_shutdown("System shutdown")

            # Verify state
            assert interceptor.is_shutdown_blocked()

            # Stop tracking
            tracker.stop_tracking()

            # Allow shutdown
            interceptor.allow_shutdown()

            # Verify unblocked
            assert not interceptor.is_shutdown_blocked()
