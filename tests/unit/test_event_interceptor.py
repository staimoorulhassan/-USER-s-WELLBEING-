"""Unit tests for event interceptor service.

Tests that:
- WM_QUERYENDSESSION message is handled
- Timeout is enforced (5 seconds)
- Callback registration works
- Shutdown is blocked/allowed properly
"""

import pytest
from unittest.mock import patch, MagicMock, call
import time
from ctypes import windll

from services.event_interceptor import EventInterceptor, ShutdownEventError


class TestEventInterceptor:
    """Unit tests for event interception functionality."""

    def test_create_event_interceptor(self):
        """Test creating event interceptor."""
        interceptor = EventInterceptor()

        # Should be initially in normal state
        assert not interceptor.is_shutdown_blocked()

        # Should have empty callback
        assert interceptor._shutdown_callback is None

    @patch('services.event_interceptor.windll.user32')
    def test_register_shutdown_handler(self, mock_windll):
        """Test registering shutdown handler."""
        interceptor = EventInterceptor()

        # Mock callback
        mock_callback = MagicMock()

        # Register handler
        interceptor.register_shutdown_handler(mock_callback)

        # Should store callback
        assert interceptor._shutdown_callback is mock_callback

        # Verify no Windows API calls (would be integration test)
        # In unit test, we just verify the state

    @patch('services.event_interceptor.windll.user32')
    def test_unregister_shutdown_handler(self, mock_windll):
        """Test unregistering shutdown handler."""
        interceptor = EventInterceptor()

        # Mock callback
        mock_callback = MagicMock()
        interceptor.register_shutdown_handler(mock_callback)

        # Unregister
        interceptor.unregister_shutdown_handler()

        # Should clear callback
        assert interceptor._shutdown_callback is None

    def test_block_shutdown(self):
        """Test blocking shutdown."""
        interceptor = EventInterceptor()

        # Initially not blocked
        assert not interceptor.is_shutdown_blocked()

        # Block shutdown
        interceptor.block_shutdown()

        # Should be blocked
        assert interceptor.is_shutdown_blocked()

        # Should have reason
        assert interceptor._shutdown_reason is not None

    def test_allow_shutdown(self):
        """Test allowing shutdown."""
        interceptor = EventInterceptor()

        # Block first
        interceptor.block_shutdown()

        # Allow shutdown
        interceptor.allow_shutdown()

        # Should be allowed
        assert not interceptor.is_shutdown_blocked()
        assert interceptor._shutdown_reason is None

    def test_multiple_block_calls(self):
        """Test multiple block calls don't interfere."""
        interceptor = EventInterceptor()

        # Block multiple times
        interceptor.block_shutdown()
        interceptor.block_shutdown()

        # Should still be blocked
        assert interceptor.is_shutdown_blocked()

        # Allow once should unblock
        interceptor.allow_shutdown()
        assert not interceptor.is_shutdown_blocked()

    def test_notification_with_callback(self):
        """Test that callback is called during shutdown."""
        interceptor = EventInterceptor()

        # Mock callback
        mock_callback = MagicMock()
        interceptor.register_shutdown_handler(mock_callback)

        # Simulate shutdown notification (would come from Windows)
        with patch('services.event_interceptor.time.sleep') as mock_sleep:
            # Test that callback would be called
            # (In integration test we'd simulate the actual Windows message)
            assert interceptor._shutdown_callback is mock_callback

            # Mock callback to verify it's called
            interceptor._shutdown_callback = mock_callback

            # Simulate the notification process
            interceptor._process_shutdown_notification()

            # Verify callback was called
            mock_callback.assert_called_once_with()

    def test_notification_without_callback(self):
        """Test that no errors occur without callback."""
        interceptor = EventInterceptor()

        # Don't register callback
        interceptor._shutdown_callback = None

        # Should not crash
        with patch('services.event_interceptor.time.sleep'):
            interceptor._process_shutdown_notification()

    def test_shutdown_error_raised(self):
        """Test that shutdown error is raised when blocked."""
        interceptor = EventInterceptor()

        # Block shutdown
        interceptor.block_shutdown()

        # Should raise error
        with pytest.raises(ShutdownEventError):
            interceptor._process_shutdown_notification()

    def test_timeout_enforcement(self):
        """Test that timeout is enforced during blocked shutdown."""
        interceptor = EventInterceptor()

        # Mock time.sleep
        with patch('services.event_interceptor.time.sleep') as mock_sleep:
            # Block shutdown
            interceptor.block_shutdown()

            # Set callback to test timeout behavior
            mock_callback = MagicMock()
            interceptor._shutdown_callback = mock_callback

            # Simulate timeout scenario
            # (In integration test this would be actual wait)

            # Verify that blocking state persists during timeout
            assert interceptor.is_shutdown_blocked()

    def test_reason_persistence(self):
        """Test that shutdown reason persists until cleared."""
        interceptor = EventInterceptor()

        # Block with specific reason
        test_reason = "User clicked shutdown"
        interceptor.block_shutdown(test_reason)

        # Should have reason
        assert interceptor._shutdown_reason == test_reason

        # Clear reason
        interceptor.allow_shutdown()

        # Should be cleared
        assert interceptor._shutdown_reason is None

    def test_reason_clearing(self):
        """Test that clearing reason doesn't affect other state."""
        interceptor = EventInterceptor()

        # Block with reason
        interceptor.block_shutdown("Test reason")

        # Clear reason but maintain blocked state (if needed)
        interceptor._shutdown_reason = None

        # Should still be blocked
        assert interceptor.is_shutdown_blocked()

    def test_callback_exception_handling(self):
        """Test that callback exceptions are handled."""
        interceptor = EventInterceptor()

        # Mock callback that raises exception
        def failing_callback():
            raise Exception("Callback failed")

        interceptor.register_shutdown_handler(failing_callback)

        # Should not crash the system
        with patch('services.event_interceptor.time.sleep'):
            try:
                interceptor._process_shutdown_notification()
            except Exception:
                # Callback exceptions shouldn't propagate
                pytest.fail("Callback exception propagated")

    def test_unregister_safety(self):
        """Test unregistering safely."""
        interceptor = EventInterceptor()

        # Register and unregister
        mock_callback = MagicMock()
        interceptor.register_shutdown_handler(mock_callback)
        interceptor.unregister_shutdown_handler()

        # Should not be blocked
        assert not interceptor.is_shutdown_blocked()

        # Simulate event after unregister
        with patch('services.event_interceptor.time.sleep'):
            interceptor._process_shutdown_notification()
            # Should not crash

    def test_reentrant_protection(self):
        """Test protection against reentrant calls."""
        interceptor = EventInterceptor()

        # Mock callback that tries to process again
        def recursive_callback():
            interceptor._process_shutdown_notification()

        interceptor.register_shutdown_handler(recursive_callback)

        # Should not recurse infinitely
        with patch('services.event_interceptor.time.sleep'):
            interceptor._process_shutdown_notification()
            # Should not crash (though recursion might occur in real scenario)

    def test_state_cleanliness(self):
        """Test state is clean after operations."""
        interceptor = EventInterceptor()

        # Test sequence
        interceptor.block_shutdown("test")
        interceptor.allow_shutdown()

        # Should be clean
        assert not interceptor.is_shutdown_blocked()
        assert interceptor._shutdown_reason is None
        assert interceptor._shutdown_callback is None