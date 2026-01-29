"""Dashboard UI frame for activity tracking.

Displays tracking controls and live feed of window activity.
"""

import logging
import customtkinter as ctk
from datetime import datetime
from typing import List

from models.activity_log import ActivityLogEntry
from models.ai_models import FocusScore, DailySummary
from services.tracker import TrackerService
from services.ai_service import AIService
from services.profile_service import ProfileService
from ui.notifications import SummaryDialog, ErrorDialog, InfoDialog
from utils.log_handler import LogHandler
from config.constants import MAX_LIVE_FEED_ENTRIES

logger = logging.getLogger(__name__)


class DashboardFrame(ctk.CTkFrame):
    """Main dashboard frame with tracking controls and live feed."""

    def __init__(self, parent, profile):
        """Initialize dashboard frame.

        Args:
            parent: Parent widget (main window)
            profile: User profile for AI context
        """
        super().__init__(parent)

        self.parent = parent
        self.profile = profile
        self.tracker_service = None
        self.ai_service = None
        self.profile_service = ProfileService()
        self.log_handler = LogHandler()
        self.celebrations_enabled = True

        self._create_widgets()

    def _create_widgets(self):
        """Create dashboard widgets."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)

        # Left sidebar - Controls
        self._create_control_panel()

        # Right side - Live Feed
        self._create_live_feed()

    def _create_control_panel(self):
        """Create control panel with tracking buttons."""
        control_frame = ctk.CTkFrame(self)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Title
        title_label = ctk.CTkLabel(
            control_frame,
            text="Wellbeing Tracker",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.pack(pady=(20, 40))

        # Tracking status
        self.status_label = ctk.CTkLabel(
            control_frame,
            text="Status: Not Tracking",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        self.status_label.pack(pady=(0, 20))

        # Start/Stop buttons
        self.start_button = ctk.CTkButton(
            control_frame,
            text="Start Tracking",
            command=self._start_tracking,
            height=40,
            fg_color="green",
            hover_color="darkgreen",
        )
        self.start_button.pack(pady=(0, 10), padx=20, fill="x")

        self.stop_button = ctk.CTkButton(
            control_frame,
            text="Stop Tracking",
            command=self._stop_tracking,
            height=40,
            fg_color="red",
            hover_color="darkred",
            state="disabled",
        )
        self.stop_button.pack(pady=(0, 10), padx=20, fill="x")

        # Stop & Summarize button
        self.summarize_button = ctk.CTkButton(
            control_frame,
            text="Stop & Summarize",
            command=self._stop_and_summarize,
            height=40,
            fg_color="blue",
            hover_color="darkblue",
            state="disabled",
        )
        self.summarize_button.pack(pady=(0, 20), padx=20, fill="x")

        # Focus Score Display
        focus_score_label = ctk.CTkLabel(
            control_frame,
            text="Focus Score",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        focus_score_label.pack(pady=(20, 5))

        self.focus_score_value = ctk.CTkLabel(
            control_frame,
            text="N/A",
            font=ctk.CTkFont(size=36, weight="bold"),
        )
        self.focus_score_value.pack(pady=(0, 5))

        # Trend indicator
        self.focus_score_trend = ctk.CTkLabel(
            control_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.focus_score_trend.pack(pady=(0, 5))

        # Focus score label (Excellent/Good/Fair/etc)
        self.focus_score_label = ctk.CTkLabel(
            control_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        self.focus_score_label.pack(pady=(0, 10))

        # Celebrations status
        celebrations_frame = ctk.CTkFrame(control_frame)
        celebrations_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.celebrations_label = ctk.CTkLabel(
            celebrations_frame,
            text="🎉 Task Detection",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.celebrations_label.pack(pady=(5, 0))

        self.celebrations_status = ctk.CTkLabel(
            celebrations_frame,
            text="Active",
            font=ctk.CTkFont(size=12),
            text_color="green"
        )
        self.celebrations_status.pack(pady=(0, 5))

    def _create_live_feed(self):
        """Create live feed component."""
        feed_frame = ctk.CTkFrame(self)
        feed_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Title
        feed_title = ctk.CTkLabel(
            feed_frame,
            text="Live Activity Feed",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        feed_title.pack(pady=(20, 10))

        # Scrollable frame for entries
        self.scrollable_frame = ctk.CTkScrollableFrame(
            feed_frame, height=400, label_text="Recent Windows"
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Initial placeholder message
        self.placeholder_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Start tracking to see activity...",
            text_color="gray",
        )
        self.placeholder_label.pack(pady=20)

    def _start_tracking(self):
        """Handle Start Tracking button click."""
        try:
            # Create tracker service if needed
            if self.tracker_service is None:
                self.tracker_service = TrackerService()

            # Create AI service if needed
            if self.ai_service is None:
                try:
                    self.ai_service = AIService()
                    logger.info("AI service initialized")
                except Exception as e:
                    logger.warning(f"AI service not available: {e}")
                    self.ai_service = None

            # Start tracking
            self.tracker_service.start_tracking()

            # Update UI state
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.summarize_button.configure(state="normal")
            self.status_label.configure(text="Status: Tracking", text_color="green")

            logger.info("Tracking started from UI")

            # Start UI update loop
            self._update_live_feed()

            # Start focus score update loop
            self._update_focus_score()

        except Exception as e:
            logger.error(f"Failed to start tracking: {e}")
            self._show_error(f"Failed to start tracking: {e}")

    def _stop_tracking(self):
        """Handle Stop Tracking button click."""
        try:
            if self.tracker_service:
                self.tracker_service.stop_tracking()

            # Update UI state
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.summarize_button.configure(state="disabled")
            self.status_label.configure(text="Status: Not Tracking", text_color="gray")

            logger.info("Tracking stopped from UI")

            # Calculate final focus score
            if self.ai_service:
                self._calculate_and_display_focus_score()

        except Exception as e:
            logger.error(f"Failed to stop tracking: {e}")
            self._show_error(f"Failed to stop tracking: {e}")

    def _stop_and_summarize(self):
        """Handle Stop & Summarize button click."""
        try:
            # Stop tracking first
            if self.tracker_service and self.tracker_service.is_tracking():
                self.tracker_service.stop_tracking()

            # Update UI state
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.summarize_button.configure(state="disabled")
            self.status_label.configure(text="Status: Generating Summary...", text_color="blue")

            logger.info("Generating daily summary")

            # Show loading indicator
            self.status_label.configure(text="Status: Generating Summary...", text_color="blue")

            # Generate summary
            self._generate_and_show_summary()

            # Update status
            self.status_label.configure(text="Status: Not Tracking", text_color="gray")

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            self.status_label.configure(text="Status: Error", text_color="red")
            ErrorDialog(self, "Summary Generation Failed", f"Failed to generate summary: {e}")

    def _generate_and_show_summary(self):
        """Generate daily summary and display in dialog.

        Handles empty logs, AI errors, and displays summary dialog.
        """
        if not self.ai_service:
            InfoDialog(self, "AI Service Unavailable", "The AI service is not configured. Please check your API key.")
            return

        # Get all activity logs
        all_logs = self.log_handler.get_all_entries()

        if not all_logs:
            InfoDialog(self, "No Activity", "No activity has been tracked yet. Start tracking and come back later!")
            return

        try:
            # Convert log dicts to ActivityLogEntry objects
            from models.activity_log import ActivityLogEntry
            activity_logs = [ActivityLogEntry.from_dict(log) for log in all_logs]

            # Generate summary
            summary = self.ai_service.generate_daily_summary(activity_logs, self.profile)

            if summary is None:
                ErrorDialog(self, "Summary Generation Failed", "Could not generate summary. The AI service may be unavailable.")
                return

            # Display summary dialog
            SummaryDialog(self, summary)

            logger.info("Daily summary displayed successfully")

        except Exception as e:
            logger.error(f"Error generating summary: {e}", exc_info=True)
            ErrorDialog(self, "Summary Generation Failed", f"An error occurred: {e}")

    def _update_live_feed(self):
        """Update live feed with recent activity.

        Called periodically using root.after() for thread-safe UI updates.
        """
        if not self.tracker_service or not self.tracker_service.is_tracking():
            return

        # Get recent activity from tracker
        recent_entries = self.tracker_service.get_recent_activity(
            limit=MAX_LIVE_FEED_ENTRIES
        )

        # Clear placeholder if present
        if hasattr(self, "placeholder_label") and self.placeholder_label:
            self.placeholder_label.pack_forget()
            self.placeholder_label = None

        # Clear existing entries
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Add entries to feed
        for entry in recent_entries:
            self._add_feed_entry(entry)

        # Schedule next update (every 2 seconds)
        self.after(2000, self._update_live_feed)

    def _update_focus_score(self):
        """Periodically update focus score display.

        Called every 5 minutes while tracking, or when activity count changes significantly.
        """
        if not self.tracker_service or not self.tracker_service.is_tracking():
            return

        # Calculate and display focus score
        if self.ai_service:
            self._calculate_and_display_focus_score()

        # Schedule next update (5 minutes)
        self.after(300000, self._update_focus_score)

    def _calculate_and_display_focus_score(self):
        """Calculate focus score and update display.

        Handles AI failures gracefully with cached score or N/A.
        """
        if not self.ai_service:
            self._display_focus_score(None)
            return

        try:
            # Get recent activity logs
            recent_logs = self.tracker_service.get_recent_activity(limit=50)

            if not recent_logs:
                self._display_focus_score(None)
                return

            # Calculate focus score
            score = self.ai_service.calculate_focus_score(recent_logs, self.profile)

            # Get the full FocusScore object
            score_obj = self.ai_service.get_latest_focus_score_object()

            # Display the score
            self._display_focus_score(score_obj)

        except Exception as e:
            logger.error(f"Failed to calculate focus score: {e}")
            # Show cached score or N/A
            cached = self.ai_service.get_latest_focus_score_object()
            if cached:
                self._display_focus_score(cached, show_error=True)
            else:
                self._display_focus_score(None)

    def _display_focus_score(self, score_obj: Optional[FocusScore], show_error: bool = False):
        """Display focus score on dashboard.

        Args:
            score_obj: FocusScore object to display
            show_error: If True, show error indicator
        """
        if score_obj is None:
            # No score available
            self.focus_score_value.configure(
                text="N/A",
                text_color="gray",
            )
            self.focus_score_trend.configure(text="")
            self.focus_score_label.configure(text="No data yet")
            return

        # Display score value
        score_value = int(score_obj.value)
        color = score_obj.get_color()
        label = score_obj.get_label()

        # Map color names to CustomTkinter colors
        color_map = {
            "green": "#2CC985",
            "yellow": "#FFD93D",
            "orange": "#FF9F1C",
            "red": "#FF5252",
        }
        text_color = color_map.get(color, "gray")

        if show_error:
            # Show error indicator
            self.focus_score_value.configure(
                text=str(score_value),
                text_color=text_color,
            )
            self.focus_score_trend.configure(
                text="⚠️ Using cached",
                text_color="orange",
            )
        else:
            self.focus_score_value.configure(
                text=str(score_value),
                text_color=text_color,
            )

            # Display trend
            trend_icons = {"up": "↑", "down": "↓", "stable": "→", "none": ""}
            trend_icon = trend_icons.get(score_obj.trend, "")
            if trend_icon:
                trend_text = f"{trend_icon} {score_obj.trend.title()}"
                if score_obj.previous_score:
                    trend_text += f" (was {int(score_obj.previous_score)})"
                self.focus_score_trend.configure(text=trend_text)
            else:
                self.focus_score_trend.configure(text="")

        # Display label
        self.focus_score_label.configure(text=label)

    def _add_feed_entry(self, entry: ActivityLogEntry):
        """Add a single entry to the live feed.

        Args:
            entry: ActivityLogEntry to display
        """
        entry_frame = ctk.CTkFrame(self.scrollable_frame)
        entry_frame.pack(fill="x", pady=5, padx=5)

        # Window title
        title_label = ctk.CTkLabel(
            entry_frame,
            text=entry.window_title,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        title_label.pack(fill="x", padx=10, pady=(5, 0))

        # Metadata (time and application)
        time_str = entry.timestamp.strftime("%H:%M:%S")
        metadata_label = ctk.CTkLabel(
            entry_frame,
            text=f"{time_str} • {entry.application} • {entry.duration_seconds}s",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
        )
        metadata_label.pack(fill="x", padx=10, pady=(0, 5))

    def _show_error(self, message: str):
        """Show error message to user.

        Args:
            message: Error message to display
        """
        # Simple alert for now (could be enhanced to a proper dialog)
        self.status_label.configure(text=f"Error: {message}", text_color="red")

    def cleanup(self):
        """Clean up resources when dashboard is destroyed."""
        if self.tracker_service and self.tracker_service.is_tracking():
            self.tracker_service.stop_tracking()
            logger.info("Stopped tracking during cleanup")
