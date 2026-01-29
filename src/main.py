"""Main application entry point for Wellbeing desktop tracker."""

import sys
import signal
import os
from pathlib import Path

import customtkinter as ctk

# Add src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env file
from dotenv import load_dotenv
dotenv_path = Path(__file__).parent.parent / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path)
    print(f"Loaded environment variables from {dotenv_path}")
else:
    print(f"Warning: .env file not found at {dotenv_path}")

from ui.main_window import MainWindow
from utils.logger import setup_logging
from utils.path_helper import initialize_data_directory

try:
    from services.instance_manager import InstanceManager
except ImportError:
    InstanceManager = None
    print("Warning: InstanceManager not available - single instance enforcement disabled")


def main():
    """Main entry point for the Wellbeing application.

    Initializes logging, data directory, checks for existing instances,
    and launches the UI.
    """
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Wellbeing application")

    # Initialize data directory
    if not initialize_data_directory():
        logger.error("Failed to initialize data directory. Exiting.")
        sys.exit(1)

    # Single instance enforcement
    instance_manager = None
    if InstanceManager:
        try:
            instance_manager = InstanceManager()

            if not instance_manager.is_first_instance():
                logger.info("Another instance is already running")

                # Try to activate existing window
                if instance_manager.activate_existing_instance():
                    logger.info("Activated existing instance")
                else:
                    logger.warning("Could not activate existing instance")

                # Show info message to user
                try:
                    import tkinter.messagebox as messagebox
                    root = ctk.CTk()
                    root.withdraw()  # Hide the window
                    messagebox.showinfo(
                        "Wellbeing Already Running",
                        "Wellbeing Desktop Tracker is already running.\n"
                        "The existing window has been brought to the foreground."
                    )
                    root.destroy()
                except Exception as e:
                    logger.error(f"Failed to show message box: {e}")

                sys.exit(0)

        except Exception as e:
            logger.error(f"Instance check failed: {e}")
            # Allow application to start if instance check fails
            print(f"Warning: Could not enforce single instance: {e}")

    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Create and launch main window
    try:
        app = MainWindow()
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    finally:
        # Cleanup instance manager
        if instance_manager:
            try:
                instance_manager.cleanup()
            except Exception as e:
                logger.error(f"Failed to cleanup instance manager: {e}")

    logger.info("Wellbeing application shutdown complete")


if __name__ == "__main__":
    main()
