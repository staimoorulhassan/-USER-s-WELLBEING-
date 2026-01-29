"""Shutdown prompt dialog for system event interception.

Shows a summary of current session when shutdown is detected.
"""

import logging
import threading
import time
import customtkinter as ctk
from typing import Optional

from models.work_state import WorkState
from services.tracker import TrackerService
from services.ai_service import AIService
from services.profile_service import ProfileService

logger = logging.getLogger(__name__)


class ShutdownPromptDialog(ctk.CTkToplevel):
    """Modal dialog for handling system shutdown events."""

    def __init__(self, parent, event_interceptor):
        """Initialize shutdown prompt dialog.

        Args:
            parent: Parent window
            event_interceptor: EventInterceptor instance
        """
        super().__init__(parent)

        self.event_interceptor = event_interceptor
        self.parent = parent
        self.tracker_service = None
        self.profile_service = ProfileService()
        self.ai_service = AIService()
        self.countdown_value = 5
        self.countdown_active = True
        self.summary_generated = False

        self._create_widgets()
        self._center_window()
        self._start_countdown()
        self._load_session_data()

        # Make modal
        self.grab_set()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Window configuration
        self.title("System Shutdown Detected")
        self.geometry("600x500")

        # Main container
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title with warning icon
        title_frame = ctk.CTkFrame(container)
        title_frame.pack(fill="x", pady=(0, 20))

        title_label = ctk.CTkLabel(
            title_frame,
            text="⚠️ System Shutdown Detected",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FF9500"
        )
        title_label.pack(pady=10)

        # Session summary section
        summary_frame = ctk.CTkFrame(container)
        summary_frame.pack(fill="both", expand=True, pady=(0, 20))

        summary_label = ctk.CTkLabel(
            summary_frame,
            text="Current Session Summary:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        summary_label.pack(pady=(10, 5))

        # Session details
        self.session_text = ctk.CTkTextbox(summary_frame, height=150, wrap="word")
        self.session_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Countdown timer
        self.countdown_label = ctk.CTkLabel(
            container,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FF9500"
        )
        self.countdown_label.pack(pady=(0, 20))

        # Buttons
        button_frame = ctk.CTkFrame(container)
        button_frame.pack(fill="x", pady=(0, 10))

        # Generate summary button
        self.summary_button = ctk.CTkButton(
            button_frame,
            text="Generate AI Summary",
            command=self._generate_summary,
            width=200,
            height=40
        )
        self.summary_button.pack(side="left", padx=10)

        # Allow shutdown button
        self.allow_button = ctk.CTkButton(
            button_frame,
            text="Allow Shutdown",
            command=self._allow_shutdown,
            width=200,
            height=40
        )
        self.allow_button.pack(side="right", padx=10)

        # Summary display area (initially hidden)
        self.summary_display_frame = None

    def _load_session_data(self):
        """Load current session data for summary."""
        try:
            # Get current tracking state
            if hasattr(self.parent, 'dashboard_frame') and self.parent.dashboard_frame:
                self.tracker_service = self.parent.dashboard_frame.tracker_service

            # Load user profile for AI context
            profile = self.profile_service.load_profile()
            if profile:
                self._display_session_info(profile)
            else:
                self.session_text.insert("1.0", "No user profile found.")
        except Exception as e:
            logger.error(f"Failed to load session data: {e}")
            self.session_text.insert("1.0", "Error loading session data.")

    def _display_session_info(self, profile):
        """Display current session information."""
        session_info = f"User: {profile.name}\n"
        session_info += f"Role: {profile.role}\n"
        session_info += f"Goal: {profile.main_goal}\n\n"

        # Add tracking info if available
        if self.tracker_service and hasattr(self.tracker_service, 'is_tracking') and self.tracker_service.is_tracking():
            session_info += "Status: Tracking in progress\n"
            session_info += "Activities will be saved before shutdown.\n\n"
        else:
            session_info += "Status: Not currently tracking\n\n"

        # Add work state if available
        if hasattr(self.parent, 'state_manager') and self.parent.state_manager:
            try:
                work_state = self.parent.state_manager.load_work_state()
                if work_state and work_state.session_summary:
                    session_info += f"Previous sessions: {work_state.streak_count} productive streaks\n"
                    if work_state.focus_score:
                        session_info += f"Recent focus score: {work_state.focus_score}/100\n"
            except Exception as e:
                logger.error(f"Failed to load work state: {e}")

        self.session_text.insert("1.0", session_info)
        self.session_text.configure(state="disabled")

    def _start_countdown(self):
        """Start the countdown timer."""
        def countdown():
            while self.countdown_active and self.countdown_value > 0:
                self.countdown_label.configure(
                    text=f"System will shutdown automatically in: {self.countdown_value}s"
                )
                time.sleep(1)
                self.countdown_value -= 1

            if self.countdown_active and self.countdown_value == 0:
                self._allow_shutdown()

        threading.Thread(target=countdown, daemon=True).start()

    def _generate_summary(self):
        """Generate AI summary of current session."""
        if self.summary_generated:
            return

        self.summary_button.configure(state="disabled")
        self.summary_button.configure(text="Generating...")

        try:
            # Get recent activity logs
            activity_logs = []
            if hasattr(self.parent, 'dashboard_frame') and self.parent.dashboard_frame:
                if hasattr(self.parent.dashboard_frame, 'live_feed') and self.parent.dashboard_frame.live_feed:
                    # Get recent logs from live feed
                    recent_logs = self.parent.dashboard_frame.live_feed.get_recent_logs(limit=50)
                    activity_logs.extend(recent_logs)

            if not activity_logs:
                self._show_summary_error("No activity data found for analysis.")
                return

            # Generate summary using AI service
            summary = self.ai_service.generate_daily_summary(activity_logs)

            # Display summary
            self._display_summary(summary)

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            self._show_summary_error("Failed to generate AI summary.")

    def _show_summary_error(self, message: str):
        """Show error message for summary generation."""
        self.summary_button.configure(state="normal")
        self.summary_button.configure(text="Generate AI Summary")

        # Show error in a small dialog
        from tkinter import messagebox
        messagebox.showerror("Summary Error", message)

    def _display_summary(self, summary):
        """Display the generated summary."""
        # Create summary display frame if it doesn't exist
        if self.summary_display_frame is None:
            self.summary_display_frame = ctk.CTkFrame(self)
            self.summary_display_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Clear existing content
        for widget in self.summary_display_frame.winfo_children():
            widget.destroy()

        # Add summary content
        title_label = ctk.CTkLabel(
            self.summary_display_frame,
            text="📊 AI-Generated Summary",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        # Summary text
        summary_text = ctk.CTkTextbox(self.summary_display_frame, height=200, wrap="word")
        summary_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        summary_text.insert("1.0", summary.summary_text)
        summary_text.configure(state="disabled")

        # Recommendations if available
        if summary.recommendations:
            recs_label = ctk.CTkLabel(
                self.summary_display_frame,
                text="💡 Recommendations:",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            recs_label.pack(pady=(10, 5))

            recs_text = "\n".join(f"• {rec}" for rec in summary.recommendations)
            recs_display = ctk.CTkTextbox(self.summary_display_frame, height=100, wrap="word")
            recs_display.pack(fill="x", padx=10, pady=(0, 10))
            recs_display.insert("1.0", recs_text)
            recs_display.configure(state="disabled")

        self.summary_generated = True
        self.summary_button.configure(text="Summary Generated")

    def _allow_shutdown(self):
        """Allow system shutdown."""
        self.countdown_active = False
        self.event_interceptor.allow_shutdown()
        self.destroy()

    def _generate_summary_and_close(self):
        """Generate summary and then allow shutdown."""
        self._generate_summary()
        # Small delay to let user see the summary
        self.after(2000, self._allow_shutdown)

    def destroy(self):
        """Clean up before destroying dialog."""
        self.countdown_active = False
        self.event_interceptor.allow_shutdown()
        super().destroy()