"""Instance manager for single-instance application enforcement.

Uses Windows named mutex with file-based fallback to ensure only one
application instance runs per user session.
"""

import logging
import os
import atexit
from pathlib import Path
from typing import Optional

try:
    import win32api
    import win32event
    import win32con
    import win32gui
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    logging.warning("pywin32 not available - using file-based locking only")

from config.constants import WELLBEING_DIR
from utils.exceptions import InstanceError

logger = logging.getLogger(__name__)

# Windows-specific constants
MUTEX_NAME = "Wellbeing_Desktop_Tracker_Single_Instance"
WM_USER_ACTIVATE = win32con.WM_USER + 1  # Custom message to activate window
WINDOW_TITLE = "Wellbeing - Desktop Tracker"


class InstanceManager:
    """Manager for single-instance application enforcement."""

    def __init__(self):
        """Initialize instance manager.

        Creates mutex or lock file on initialization.
        """
        self.mutex = None
        self.lock_file_path = WELLBEING_DIR / ".lock"

        # Try to create mutex on Windows
        if HAS_WIN32:
            self.mutex = self._create_mutex()

        # If mutex creation failed or not on Windows, use file-based fallback
        if self.mutex is None:
            self._use_file_lock = True
            self._acquire_file_lock()
        else:
            self._use_file_lock = False

        # Register cleanup on exit
        atexit.register(self.cleanup)

    def _create_mutex(self) -> Optional[object]:
        """Create or open Windows named mutex.

        Returns:
            Mutex handle if first instance, None if mutex already exists or creation failed
        """
        if not HAS_WIN32:
            return None

        try:
            # Try to create mutex with initial ownership
            # ERROR_ALREADY_EXISTS = 183
            mutex = win32event.CreateMutex(None, False, MUTEX_NAME)
            error_code = win32api.GetLastError()

            if error_code == 183:  # ERROR_ALREADY_EXISTS
                logger.info("Another instance is already running (mutex exists)")
                win32api.CloseHandle(mutex)
                return None

            logger.info("Created mutex for single-instance enforcement")
            return mutex

        except Exception as e:
            logger.error(f"Failed to create mutex: {e}")
            return None

    def _acquire_file_lock(self) -> None:
        """Acquire file-based lock (fallback method).

        Creates a lock file with current PID.
        """
        try:
            # Clean up stale lock file if needed
            self._cleanup_stale_lock()

            # Create lock file with current PID
            with open(self.lock_file_path, "w") as f:
                f.write(str(os.getpid()))

            logger.info(f"Created lock file: {self.lock_file_path}")

        except Exception as e:
            logger.error(f"Failed to create lock file: {e}")
            raise InstanceError(f"Could not acquire lock: {e}") from e

    def _cleanup_stale_lock(self) -> None:
        """Clean up stale lock file if process is not running.

        Checks if the PID in the lock file is still running.
        """
        if not self.lock_file_path.exists():
            return

        try:
            with open(self.lock_file_path, "r") as f:
                pid_str = f.read().strip()

            if not pid_str:
                # Empty lock file, remove it
                self.lock_file_path.unlink()
                logger.info("Removed empty lock file")
                return

            pid = int(pid_str)

            # Check if process is running
            if self._is_process_running(pid):
                logger.info(f"Process {pid} is still running")
            else:
                # Process not running, clean up stale lock
                self.lock_file_path.unlink()
                logger.info(f"Removed stale lock file for PID {pid}")

        except (ValueError, FileNotFoundError) as e:
            logger.debug(f"Could not check lock file: {e}")
        except Exception as e:
            logger.error(f"Error cleaning up stale lock: {e}")

    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with the given PID is running.

        Args:
            pid: Process ID to check

        Returns:
            True if process is running, False otherwise
        """
        if HAS_WIN32:
            try:
                # Try to open process with PROCESS_QUERY_INFORMATION
                handle = win32api.OpenProcess(
                    win32con.PROCESS_QUERY_INFORMATION, False, pid
                )
                if handle:
                    win32api.CloseHandle(handle)
                    return True
            except win32api.error as e:
                if e.winerror == 87:  # ERROR_INVALID_PARAMETER
                    return False
                # Other errors, assume process is running
                return True
        else:
            # Unix-like fallback
            try:
                os.kill(pid, 0)  # Signal 0 doesn't kill, just checks existence
                return True
            except (OSError, ProcessLookupError):
                return False

        return False

    def is_first_instance(self) -> bool:
        """Check if this is the first application instance.

        Returns:
            True if this is the first instance, False otherwise
        """
        if self.mutex is not None:
            # Mutex was successfully created
            return True
        elif self._use_file_lock:
            # File lock was successfully created
            return True
        else:
            # Neither mutex nor file lock was created
            return False

    def activate_existing_instance(self) -> bool:
        """Activate existing application instance.

        Finds the main window and brings it to foreground.

        Returns:
            True if window was found and activated, False otherwise
        """
        if not HAS_WIN32:
            logger.warning("Window activation requires Windows")
            return False

        try:
            # Find window by title
            hwnd = win32gui.FindWindow(None, WINDOW_TITLE)

            if not hwnd:
                logger.warning(f"Could not find window: {WINDOW_TITLE}")
                return False

            # Check if window is minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                logger.info("Restored minimized window")

            # Bring window to foreground
            win32gui.SetForegroundWindow(hwnd)
            logger.info("Brought window to foreground")

            # Flash window to get user attention
            flash_info = (
                16,  # sizeof(FLASHWINFO)
                hwnd,
                win32con.FLASHW_ALL | win32con.FLASHW_TIMERNOFG,
                3,  # flash count
                0,  # flash timeout (default)
            )
            win32gui.FlashWindowEx(flash_info)
            logger.info("Flashed window taskbar button")

            return True

        except Exception as e:
            logger.error(f"Failed to activate existing instance: {e}")
            return False

    def cleanup(self) -> None:
        """Clean up mutex and lock file resources.

        Called automatically on exit via atexit.
        """
        # Close mutex handle
        if self.mutex is not None:
            try:
                win32api.CloseHandle(self.mutex)
                logger.info("Closed mutex handle")
            except Exception as e:
                logger.error(f"Failed to close mutex: {e}")
            finally:
                self.mutex = None

        # Remove lock file
        if self._use_file_lock and self.lock_file_path.exists():
            try:
                self.lock_file_path.unlink()
                logger.info("Removed lock file")
            except Exception as e:
                logger.error(f"Failed to remove lock file: {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()
