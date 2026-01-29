"""System event interceptor service.

Intercepts shutdown/restart/sleep events and provides hooks for the application to respond.
"""

import logging
import time
from typing import Optional, Callable
import threading

try:
    import win32con
    import win32gui
    import win32api
    from ctypes import windll
except ImportError:
    win32con = None
    win32gui = None
    win32api = None
    windll = None

from utils.exceptions import EventInterceptorError

logger = logging.getLogger(__name__)


class ShutdownEventError(Exception):
    """Raised when shutdown is blocked."""
    pass


class EventInterceptor:
    """Service for intercepting system events like shutdown/restart/sleep."""

    def __init__(self):
        """Initialize event interceptor."""
        if win32gui is None:
            raise EventInterceptorError("pywin32 is required for event interception")

        self._shutdown_callback: Optional[Callable] = None
        self._shutdown_blocked = False
        self._shutdown_reason: Optional[str] = None
        self._message_processing_thread: Optional[threading.Thread] = None
        self._stop_processing = threading.Event()
        self._message_loop_active = False

        # Windows message constants
        self.WM_QUERYENDSESSION = 0x0011  # WM_QUERYENDSESSION
        self.WM_ENDSESSION = 0x0016       # WM_ENDSESSION

        logger.info("Event interceptor initialized")

    def register_shutdown_handler(self, callback: Callable) -> None:
        """Register callback for shutdown events.

        Args:
            callback: Function to call when shutdown is detected

        Raises:
            EventInterceptorError: If callback is not callable
        """
        if not callable(callback):
            raise EventInterceptorError("Shutdown callback must be callable")

        self._shutdown_callback = callback
        logger.info("Shutdown handler registered")

    def unregister_shutdown_handler(self) -> None:
        """Unregister shutdown handler."""
        self._shutdown_callback = None
        logger.info("Shutdown handler unregistered")

    def block_shutdown(self, reason: Optional[str] = None) -> None:
        """Block system shutdown with optional reason.

        Args:
            reason: Reason for blocking shutdown (optional)
        """
        self._shutdown_blocked = True
        self._shutdown_reason = reason or "Application needs to complete tasks"
        logger.info(f"Shutdown blocked: {self._shutdown_reason}")

    def allow_shutdown(self) -> None:
        """Allow system shutdown."""
        self._shutdown_blocked = False
        self._shutdown_reason = None
        logger.info("Shutdown allowed")

    def is_shutdown_blocked(self) -> bool:
        """Check if shutdown is currently blocked.

        Returns:
            True if shutdown is blocked
        """
        return self._shutdown_blocked

    def _process_shutdown_notification(self) -> None:
        """Process shutdown notification internally."""
        logger.info("Processing shutdown notification")

        # Call registered callback if available
        if self._shutdown_callback:
            try:
                self._shutdown_callback()
            except Exception as e:
                logger.error(f"Error in shutdown callback: {e}")

    def _handle_query_end_session(self, msg) -> bool:
        """Handle WM_QUERYENDSESSION message.

        Returns:
            True to allow shutdown, False to block
        """
        logger.info("Received WM_QUERYENDSESSION message")

        # Check if we need to block shutdown
        if self._shutdown_blocked:
            logger.info("Shutdown blocked by application")

            # Process the notification to trigger UI callback
            self._process_shutdown_notification()

            return False
        else:
            logger.info("Shutdown allowed by application")
            return True

    def _handle_end_session(self, msg) -> bool:
        """Handle WM_ENDSESSION message.

        Returns:
            True if session ended, False otherwise
        """
        logger.info("Received WM_ENDSESSION message")

        wparam = msg[2]  # wparam from the message
        if wparam == 0:  # End session initiated by application
            logger.info("Session ended by application")
        else:  # End session initiated by system
            logger.info("Session ended by system - shutting down")

        # Clean up resources
        self.cleanup()

        return True

    def start_message_processing(self) -> None:
        """Start Windows message processing in a separate thread."""
        if self._message_loop_active:
            logger.warning("Message processing already active")
            return

        self._stop_processing.clear()
        self._message_loop_active = True

        # Start message processing thread
        self._message_processing_thread = threading.Thread(
            target=self._message_loop,
            daemon=True,
            name="MessageProcessor"
        )
        self._message_processing_thread.start()

        logger.info("Message processing started")

    def stop_message_processing(self) -> None:
        """Stop Windows message processing."""
        self._message_loop_active = False
        self._stop_processing.set()

        if self._message_processing_thread and self._message_processing_thread.is_alive():
            self._message_processing_thread.join(timeout=2.0)

        logger.info("Message processing stopped")

    def _message_loop(self) -> None:
        """Main message processing loop using Windows messages."""
        logger.debug("Message processing loop started")

        # Register window class for message handling
        self._register_message_window()

        while not self._stop_processing.is_set():
            try:
                # Process Windows messages
                win32gui.PumpWaitingMessages()

                # Small sleep to prevent CPU hogging
                time.sleep(0.01)

                # Check shutdown state
                if self._shutdown_blocked:
                    logger.debug("Shutdown is blocked - waiting for user response")
                    # In real implementation, this would check for timeout
                    # and update UI accordingly

            except Exception as e:
                logger.error(f"Error in message loop: {e}")

        logger.debug("Message processing loop stopped")

    def _register_message_window(self) -> None:
        """Register a hidden window for Windows message handling."""
        # Window class name
        class_name = "WellbeingEventInterceptor"

        # Window procedure
        def wnd_proc(hwnd, msg, wparam, lparam):
            if msg == self.WM_QUERYENDSESSION:
                return self._handle_query_end_session((hwnd, msg, wparam, lparam))
            elif msg == self.WM_ENDSESSION:
                return self._handle_end_session((hwnd, msg, wparam, lparam))
            return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

        # Register window class
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = wnd_proc
        wc.lpszClassName = class_name
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)

        # Register class
        try:
            class_atom = win32gui.RegisterClass(wc)

            # Create hidden window
            self._message_hwnd = win32gui.CreateWindowEx(
                0,  # No extended styles
                class_name,
                "Wellbeing Event Interceptor",  # Window name
                0,  # Window style
                0, 0, 1, 1,  # Position and size (1x1 pixel)
                0,  # Parent window
                0,  # Menu
                wc.hInstance,
                None  # Additional data
            )

            logger.info("Message window registered successfully")
        except Exception as e:
            logger.error(f"Failed to register message window: {e}")
            self._message_hwnd = None

    def simulate_shutdown_event(self) -> None:
        """Simulate receiving a shutdown event (for testing)."""
        logger.info("Simulating shutdown event")

        # In real implementation, this would come from Windows message
        if self._shutdown_blocked:
            logger.info("Shutdown event detected - blocked")
        else:
            logger.info("Shutdown event detected - allowed")

        self._process_shutdown_notification()

    def get_shutdown_reason(self) -> Optional[str]:
        """Get the reason why shutdown is blocked.

        Returns:
            Reason string or None if not blocked
        """
        return self._shutdown_reason

    def is_callback_registered(self) -> bool:
        """Check if a shutdown callback is registered.

        Returns:
            True if callback is registered
        """
        return self._shutdown_callback is not None

    def cleanup(self) -> None:
        """Clean up resources."""
        logger.info("Cleaning up event interceptor")

        # Destroy message window if it exists
        if hasattr(self, '_message_hwnd') and self._message_hwnd:
            try:
                win32gui.DestroyWindow(self._message_hwnd)
                self._message_hwnd = None
                logger.info("Message window destroyed")
            except Exception as e:
                logger.error(f"Error destroying message window: {e}")

        # Stop message processing
        self.stop_message_processing()

        # Allow any pending shutdown
        if self._shutdown_blocked:
            self.allow_shutdown()

        # Unregister callback
        self.unregister_shutdown_handler()

        logger.info("Event interceptor cleanup complete")


# Global instance for the application
_event_interceptor: Optional[EventInterceptor] = None


def get_event_interceptor() -> EventInterceptor:
    """Get or create the global event interceptor instance."""
    global _event_interceptor

    if _event_interceptor is None:
        _event_interceptor = EventInterceptor()

    return _event_interceptor


def initialize_event_interceptor() -> EventInterceptor:
    """Initialize and start the event interceptor."""
    interceptor = get_event_interceptor()
    interceptor.start_message_processing()
    return interceptor


def shutdown_event_interceptor() -> None:
    """Shut down the event interceptor."""
    global _event_interceptor

    if _event_interceptor is not None:
        _event_interceptor.cleanup()
        _event_interceptor = None