"""Base main window component using CustomTkinter.

Provides the application's main window skeleton.
"""

import logging
import customtkinter as ctk

from services.profile_service import ProfileService
from ui.onboarding import OnboardingFrame
from ui.settings import SettingsFrame
from ui.notifications import WorkStateDialog

try:
    from services.state_manager import StateManager
except ImportError:
    StateManager = None
    logging.warning("StateManager not available - work state persistence disabled")

try:
    from services.event_interceptor import EventInterceptor, initialize_event_interceptor
except ImportError:
    EventInterceptor = None
    initialize_event_interceptor = None
    logging.warning("EventInterceptor not available - shutdown interception disabled")

try:
    from ui.shutdown_prompt import ShutdownPromptDialog
except ImportError:
    ShutdownPromptDialog = None
    logging.warning("ShutdownPromptDialog not available - shutdown prompts disabled")

try:
    from services.task_detection import TaskDetectionService, initialize_task_detection
    from ui.celebration_popup import CelebrationManager
    from ui.celebration_settings import CelebrationSettingsDialog
except ImportError:
    TaskDetectionService = None
    initialize_task_detection = None
    CelebrationManager = None
    CelebrationSettingsDialog = None
    logging.warning("Task detection and celebrations not available")

logger = logging.getLogger(__name__)


class MainWindow(ctk.CTk):
    """Main application window."""

    def __init__(self):
        """Initialize main window with default configuration."""
        super().__init__()

        # Window configuration
        self.title("Wellbeing - Desktop Tracker")
        self.geometry("900x650")

        # Set appearance mode and theme
        ctk.set_appearance_mode("System")  # Options: System, Dark, Light
        ctk.set_default_color_theme("blue")  # Options: blue, dark-blue, green

        # Services
        self.profile_service = ProfileService()
        self.state_manager = StateManager() if StateManager else None
        self.event_interceptor = None
        self.task_detection_service = None
        self.celebration_manager = None

        # Initialize event interceptor for shutdown handling
        if EventInterceptor and initialize_event_interceptor:
            try:
                self.event_interceptor = initialize_event_interceptor()
                self._register_shutdown_handler()
                logger.info("Event interceptor initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize event interceptor: {e}")
                self.event_interceptor = None

        # Initialize task detection and celebrations
        if TaskDetectionService and initialize_task_detection and CelebrationManager:
            try:
                self.task_detection_service = initialize_task_detection()
                self.celebration_manager = CelebrationManager(self)
                self._register_task_detection_callback()
                logger.info("Task detection and celebrations initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize task detection: {e}")
                self.task_detection_service = None
                self.celebration_manager = None

        # Placeholder for content frames
        self.onboarding_frame = None
        self.dashboard_frame = None
        self.settings_frame = None

        # Create menu bar
        self._create_menu()

        # Determine which screen to show
        self._initialize_screen()

    def _create_menu(self):
        """Create application menu bar (placeholder for now)."""
        # CTkMenuBar is not available in this version of customtkinter
        # Creating a simple button menu as a temporary solution
        menu_frame = ctk.CTkFrame(self)
        menu_frame.pack(side="top", fill="x", padx=10, pady=5)

        # Settings button
        settings_btn = ctk.CTkButton(
            menu_frame,
            text="Settings",
            command=self.show_settings,
            width=100
        )
        settings_btn.pack(side="left", padx=5)

        # Exit button
        exit_btn = ctk.CTkButton(
            menu_frame,
            text="Exit",
            command=self.destroy,
            width=100
        )
        exit_btn.pack(side="right", padx=5)

    def _show_about(self):
        """Show about dialog."""
        from tkinter import messagebox
        messagebox.showinfo(
            "About Wellbeing",
            "Wellbeing Desktop Tracker v0.2.0\n\n"
            "A desktop application for tracking your computer activity\n"
            "and getting AI-powered insights into your work patterns.\n\n"
            "Features:\n"
            "• Real-time activity tracking\n"
            "• AI-calculated focus scores\n"
            "• Daily summaries with recommendations\n"
            "• Privacy-first (all data stored locally)"
        )

    def _initialize_screen(self):
        """Initialize appropriate screen based on profile status."""
        if self.profile_service.profile_exists():
            logger.info("Existing profile found - showing dashboard")
            self.show_dashboard()
            # Show welcome back dialog if previous session exists
            self._show_welcome_back_if_applicable()
        else:
            logger.info("No profile found - showing onboarding")
            self.show_onboarding()

    def _show_welcome_back_if_applicable(self):
        """Show welcome back dialog if previous session data exists."""
        if not self.state_manager:
            return

        try:
            work_state = self.state_manager.load_work_state()
            if work_state and work_state.session_summary:
                # Only show if there's meaningful session data
                logger.info("Showing previous session summary")
                WorkStateDialog(self, work_state)
        except Exception as e:
            logger.error(f"Failed to load work state for welcome dialog: {e}")

    def show_onboarding(self):
        """Display onboarding frame for first-time users."""
        # Clear any existing frames
        self._clear_frames()

        # Create onboarding frame
        self.onboarding_frame = OnboardingFrame(self, self._on_onboarding_complete)
        self.onboarding_frame.pack(fill="both", expand=True)

        logger.info("Onboarding screen displayed")

    def show_dashboard(self):
        """Display dashboard frame with tracking controls and live feed."""
        # Clear any existing frames
        self._clear_frames()

        # Import here to avoid circular dependency
        from ui.dashboard import DashboardFrame

        # Load user profile for AI context
        profile = self.profile_service.load_profile()
        if not profile:
            logger.error("No profile found - cannot show dashboard")
            self.show_onboarding()
            return

        # Create dashboard frame with profile
        self.dashboard_frame = DashboardFrame(self, profile)
        self.dashboard_frame.pack(fill="both", expand=True)

        logger.info("Dashboard screen displayed")

    def show_settings(self):
        """Display settings frame for profile management."""
        # Clear any existing frames
        self._clear_frames()

        # Load current profile
        profile = self.profile_service.load_profile()
        if not profile:
            logger.error("No profile found - cannot show settings")
            self.show_onboarding()
            return

        # Create settings frame
        self.settings_frame = SettingsFrame(
            self,
            profile,
            on_save_callback=self._on_settings_saved,
            on_cancel_callback=self._on_settings_canceled,
        )
        self.settings_frame.pack(fill="both", expand=True)

        logger.info("Settings screen displayed")

    def _on_settings_saved(self, updated_profile):
        """Handle settings save completion.

        Args:
            updated_profile: Updated UserProfile
        """
        logger.info(f"Settings saved for {updated_profile.name}")

        # Go back to dashboard with updated profile
        self.show_dashboard()

    def _on_settings_canceled(self):
        """Handle settings cancel."""
        logger.info("Settings changes canceled")

        # Go back to dashboard
        self.show_dashboard()

    def _on_onboarding_complete(self, profile):
        """Handle onboarding completion.

        Args:
            profile: Created UserProfile
        """
        logger.info(f"Onboarding completed for {profile.name}")
        self.show_dashboard()

    def _register_shutdown_handler(self):
        """Register shutdown handler for event interceptor."""
        if not self.event_interceptor:
            return

        def on_shutdown_detected():
            """Handle shutdown event by showing prompt."""
            self._show_shutdown_prompt()

        self.event_interceptor.register_shutdown_handler(on_shutdown_detected)

    def _show_shutdown_prompt(self):
        """Show shutdown prompt with session summary."""
        if not self.event_interceptor:
            return

        # Block shutdown while showing prompt
        self.event_interceptor.block_shutdown("Application shutdown in progress")

        # Create and show shutdown prompt dialog
        ShutdownPromptDialog(self, self.event_interceptor)

    def _register_task_detection_callback(self):
        """Register task detection callback."""
        if not self.task_detection_service:
            return

        def on_task_detected(accomplishment):
            """Handle task accomplishment detection."""
            logger.info(f"Task accomplished: {accomplishment.task_name}")

            # Show celebration popup
            if self.celebration_manager:
                self.celebration_manager.show_celebration(accomplishment)

            # Could also add animation effects here
            # self._celebration_effects.start_confetti_burst(x, y)

        self.task_detection_service.set_detection_callback(on_task_detected)

    def _clear_frames(self):
        """Remove all content frames."""
        if self.onboarding_frame:
            self.onboarding_frame.destroy()
            self.onboarding_frame = None

        if self.dashboard_frame:
            self.dashboard_frame.destroy()
            self.dashboard_frame = None

        if self.settings_frame:
            self.settings_frame.destroy()
            self.settings_frame = None

    def destroy(self):
        """Clean up resources before destroying window."""
        # Perform graceful shutdown
        self._graceful_shutdown()

        # Continue with normal destruction
        super().destroy()

    def _graceful_shutdown(self):
        """Perform graceful shutdown of the application."""
        logger.info("Starting graceful shutdown")

        # Check if we're currently tracking and save work state
        if (hasattr(self, 'dashboard_frame') and self.dashboard_frame and
            self.dashboard_frame.tracker_service and
            self.dashboard_frame.tracker_service.is_tracking()):

            logger.info("Stopping tracking before shutdown")
            self.dashboard_frame.tracker_service.stop_tracking()

        # Save any pending work state
        if self.state_manager:
            try:
                # Get current session data and save work state
                if (hasattr(self, 'dashboard_frame') and self.dashboard_frame and
                    self.dashboard_frame.tracker_service):

                    work_state = self.state_manager.determine_work_state(
                        self.dashboard_frame.tracker_service,
                        self.profile_service
                    )
                    self.state_manager.save_work_state(work_state)
            except Exception as e:
                logger.error(f"Failed to save work state during shutdown: {e}")

        # Clean up event interceptor
        if self.event_interceptor:
            self.event_interceptor.cleanup()

        # Clean up task detection service
        if self.task_detection_service:
            self.task_detection_service.cleanup()

        logger.info("Graceful shutdown complete")

    def _show_celebration_settings(self):
        """Show celebration settings dialog."""
        if not CelebrationSettingsDialog or not self.task_detection_service:
            return

        dialog = CelebrationSettingsDialog(self, self.task_detection_service)
        self.wait_window(dialog)  # Wait for dialog to close

    def _toggle_celebrations(self):
        """Toggle celebrations on/off."""
        if not self.task_detection_service:
            return

        if self.task_detection_service.is_running:
            self.task_detection_service.stop_detection()
            logger.info("Celebrations disabled")
        else:
            self.task_detection_service.start_detection()
            logger.info("Celebrations enabled")

        # Update dashboard if available
        if hasattr(self, 'dashboard_frame') and self.dashboard_frame:
            status = "Active" if self.task_detection_service.is_running else "Disabled"
            color = "green" if self.task_detection_service.is_running else "red"
            self.dashboard_frame.celebrations_status.configure(text=status, text_color=color)
