"""New dashboard UI with modern card-based layout.

Design based on specification with sidebar form and card-based main content.
"""

import logging
import customtkinter as ctk
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from models.activity_log import ActivityLogEntry
from models.ai_models import FocusScore, DailySummary
from models.profile import UserProfile
from services.tracker import TrackerService
from services.ai_service import AIService
from services.profile_service import ProfileService
from ui.notifications import SummaryDialog, ErrorDialog, InfoDialog
from utils.log_handler import LogHandler
from config.constants import MAX_LIVE_FEED_ENTRIES

logger = logging.getLogger(__name__)

# ---------- FONT SYSTEM ----------
FONT_TITLE = ("Segoe UI", 24, "bold")
FONT_CARD_TITLE = ("Segoe UI", 18, "bold")
FONT_BODY = ("Segoe UI", 14)
FONT_META = ("Segoe UI", 13)


class NewDashboardFrame(ctk.CTkFrame):
    """New dashboard frame with card-based layout."""

    def __init__(self, parent, profile: UserProfile):
        """Initialize new dashboard frame.

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

        # Tracking state
        self.is_tracking_active = False
        self.session_start_time = None

        # Configure appearance
        ctk.set_appearance_mode("light")
        ctk.deactivate_automatic_dpi_awareness()  # 🔴 VERY IMPORTANT

        self._create_widgets()

    def _create_widgets(self):
        """Create dashboard widgets with sidebar and card layout."""
        # Configure grid - 2 columns: sidebar and main content
        self.grid_columnconfigure(0, weight=0)  # Sidebar (fixed width)
        self.grid_columnconfigure(1, weight=1)  # Main content (expands)
        self.grid_rowconfigure(0, weight=1)

        # Set background
        self.configure(fg_color="#f4f6fb")

        # Left sidebar - Form
        self._create_sidebar()

        # Right main content - Cards
        self._create_main_content()

    def _create_sidebar(self):
        """Create left sidebar with profile form."""
        sidebar = ctk.CTkFrame(
            self,
            width=260,
            fg_color="#ffffff",
            corner_radius=0
        )
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        y = 20

        def label(text):
            nonlocal y
            ctk.CTkLabel(sidebar, text=text, font=FONT_META)\
                .place(x=20, y=y)
            y += 22

        def value(text):
            nonlocal y
            ctk.CTkLabel(sidebar, text=text, font=FONT_BODY)\
                .place(x=20, y=y)
            y += 28

        # Header
        ctk.CTkLabel(sidebar, text="Step 1. Dashboard", font=FONT_CARD_TITLE)\
            .place(x=20, y=y)
        y += 40

        # User info
        label("Name")
        value(self.profile.name)

        label("Role")
        value(self.profile.role)

        label("Goal")
        value(self.profile.main_goal)

        y += 10
        ctk.CTkLabel(sidebar, text="Session Info", font=FONT_CARD_TITLE)\
            .place(x=20, y=y)
        y += 32

        # Session status
        self.session_status = ctk.CTkLabel(
            sidebar,
            text="Status: Not Tracking",
            font=FONT_META
        )
        self.session_status.place(x=20, y=y)
        y += 22

        # Session time
        self.session_time = ctk.CTkLabel(
            sidebar,
            text="Time: 0 min",
            font=FONT_META
        )
        self.session_time.place(x=20, y=y)

        # Action buttons
        ctk.CTkButton(
            sidebar,
            text="Start Tracking",
            command=self._start_tracking,
            fg_color="#4CAF50",
            height=34,
            width=200
        ).place(x=30, y=520)

        ctk.CTkButton(
            sidebar,
            text="Stop Tracking",
            command=self._stop_tracking,
            fg_color="#F44336",
            height=34,
            width=200
        ).place(x=30, y=565)

    def _create_main_content(self):
        """Create main content area with cards."""
        main = ctk.CTkFrame(self, fg_color="#f5f7fb", corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main.grid_columnconfigure((0, 1, 2), weight=1)
        main.grid_rowconfigure((1, 2), weight=1)

        # Header
        ctk.CTkLabel(
            main,
            text="The Main Dashboard",
            font=FONT_TITLE
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 20))

        # Create cards
        self._create_goal_card(main)
        self._create_live_card(main)
        self._create_progress_card(main)
        self._create_summary_card(main)
        self._create_ai_card(main)

    def _create_card(self, parent):
        """Create a styled card frame."""
        return ctk.CTkFrame(
            parent,
            fg_color="#ffffff",
            corner_radius=14
        )

    def _create_goal_card(self, parent):
        """Create goal card."""
        card = self._create_card(parent)
        card.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(
            card,
            text=f"{self.profile.name}'s Wellbeing",
            font=FONT_CARD_TITLE
        ).pack(anchor="w", padx=16, pady=(14, 6))

        ctk.CTkLabel(
            card,
            text=f"Goal\n{self.profile.main_goal}",
            font=FONT_BODY,
            justify="left"
        ).pack(anchor="w", padx=16)

        ctk.CTkButton(
            card,
            text="Start →",
            width=120,
            height=34,
            corner_radius=8,
            command=self._start_tracking
        ).pack(anchor="w", padx=16, pady=12)

    def _create_live_card(self, parent):
        """Create live feed card."""
        card = self._create_card(parent)
        card.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(
            card,
            text="Live Feed",
            font=FONT_CARD_TITLE
        ).pack(anchor="w", padx=16, pady=(14, 6))

        self.activity_text = ctk.CTkLabel(
            card,
            text=f"{self.profile.name} is not currently tracking",
            font=FONT_BODY,
            wraplength=250
        )
        self.activity_text.pack(anchor="w", padx=16)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            card,
            height=6
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=16, pady=12)

    def _create_progress_card(self, parent):
        """Create progress card with multiple bars."""
        card = self._create_card(parent)
        card.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(
            card,
            text="Session Progress",
            font=FONT_CARD_TITLE
        ).pack(anchor="w", padx=16, pady=(14, 6))

        # Store progress bars for updates
        self.progress_bars = {}

        progress_items = [
            ("Focus Time", "#4CAF50"),
            ("Break Time", "#FFC107"),
            ("Distraction", "#F44336")
        ]

        for label, color in progress_items:
            lbl = ctk.CTkLabel(card, text=label, font=FONT_BODY)
            lbl.pack(anchor="w", padx=16, pady=(6, 2))

            bar = ctk.CTkProgressBar(card, height=6)
            bar.set(0)
            bar.pack(fill="x", padx=16, pady=2)
            self.progress_bars[label] = bar

    def _create_summary_card(self, parent):
        """Create summary card."""
        card = self._create_card(parent)
        card.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(
            card,
            text="Session Summary",
            font=FONT_CARD_TITLE
        ).pack(anchor="w", padx=16, pady=(14, 6))

        self.summary_text = ctk.CTkLabel(
            card,
            text="No session data yet. Start tracking to see your progress.",
            font=FONT_BODY,
            justify="left",
            wraplength=600
        )
        self.summary_text.pack(anchor="w", padx=16)

    def _create_ai_card(self, parent):
        """Create AI monitoring card."""
        card = self._create_card(parent)
        card.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")

        # Avatar placeholder (circle with initials)
        avatar_frame = ctk.CTkFrame(
            card,
            fg_color="#E0E0E0",
            corner_radius=60
        )
        avatar_frame.pack(pady=(20, 10))

        initials = "".join([n[0].upper() for n in self.profile.name.split()])[:2]
        ctk.CTkLabel(
            avatar_frame,
            text=initials,
            font=FONT_BODY,
            text_color="#666666"
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            card,
            text="AI Monitoring",
            font=FONT_CARD_TITLE
        ).pack(pady=10)

        ctk.CTkButton(
            card,
            text="Finish & Summarize",
            command=self._finish_and_summarize,
            height=30,
            width=160
        ).pack(pady=12)

        # Status indicator
        self.status_label = ctk.CTkLabel(
            card,
            text="● Not Tracking",
            font=FONT_META
        )
        self.status_label.pack(pady=(0, 10))

        # Celebrations status (for compatibility)
        self.celebrations_status = ctk.CTkLabel(
            card,
            text="Active",
            font=FONT_META,
            text_color="#4CAF50"
        )

    def _start_tracking(self):
        """Handle Start Tracking button click."""
        try:
            if self.tracker_service is None:
                self.tracker_service = TrackerService()

            if self.ai_service is None:
                try:
                    self.ai_service = AIService()
                    logger.info("AI service initialized")
                except Exception as e:
                    logger.warning(f"AI service not available: {e}")
                    self.ai_service = None

            self.tracker_service.start_tracking()
            self.is_tracking_active = True
            self.session_start_time = datetime.now()

            # Update UI
            self.status_label.configure(text="● Tracking Active", text_color="#4CAF50")
            self.session_status.configure(text="Status: Tracking Active")
            self.activity_text.configure(
                text=f"{self.profile.name} is currently working on their goal..."
            )

            logger.info("Tracking started from UI")

            # Start UI update loops
            self._update_live_feed()
            self._update_progress_metrics()
            self._update_session_time()

        except Exception as e:
            logger.error(f"Failed to start tracking: {e}", exc_info=True)
            ErrorDialog(self, "Error", f"Failed to start tracking: {e}")

    def _stop_tracking(self):
        """Handle Stop Tracking button click."""
        try:
            if self.tracker_service:
                self.tracker_service.stop_tracking()
                self.is_tracking_active = False

            # Calculate final metrics
            if self.ai_service:
                self._calculate_and_display_final_metrics()

            # Update UI
            self.status_label.configure(text="● Not Tracking", text_color="#999999")
            self.session_status.configure(text="Status: Not Tracking")
            self.activity_text.configure(
                text=f"{self.profile.name} has stopped tracking"
            )

            logger.info("Tracking stopped from UI")

        except Exception as e:
            logger.error(f"Failed to stop tracking: {e}", exc_info=True)
            ErrorDialog(self, "Error", f"Failed to stop tracking: {e}")

    def _finish_and_summarize(self):
        """Handle Finish & Summarize button click."""
        try:
            # Stop tracking first
            if self.is_tracking_active and self.tracker_service:
                self.tracker_service.stop_tracking()
                self.is_tracking_active = False

            self.status_label.configure(text="● Generating...", text_color="#2196F3")

            # Generate summary
            if not self.ai_service:
                InfoDialog(self, "AI Unavailable", "AI service not configured")
                self.status_label.configure(text="● Not Tracking", text_color="#999999")
                return

            all_logs = self.log_handler.get_all_entries()
            if not all_logs:
                InfoDialog(self, "No Activity", "No activity tracked yet")
                self.status_label.configure(text="● Not Tracking", text_color="#999999")
                return

            activity_logs = [ActivityLogEntry.from_dict(log) for log in all_logs]
            summary = self.ai_service.generate_daily_summary(activity_logs, self.profile)

            if summary:
                SummaryDialog(self, summary)
                logger.info("Summary displayed successfully")

            # Calculate and display final metrics
            self._calculate_and_display_final_metrics()

            self.status_label.configure(text="● Not Tracking", text_color="#999999")

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}", exc_info=True)
            ErrorDialog(self, "Error", f"Failed to generate summary: {e}")
            self.status_label.configure(text="● Error", text_color="#F44336")

    def _update_live_feed(self):
        """Update live feed with recent activity."""
        if not self.is_tracking_active or not self.tracker_service:
            return

        try:
            recent_entries = self.tracker_service.get_recent_activity(limit=1)

            if recent_entries:
                latest = recent_entries[0]
                self.activity_text.configure(
                    text=f"{self.profile.name} is currently: {latest.window_title}"
                )

                # Update progress bar based on session duration
                if self.session_start_time:
                    elapsed = (datetime.now() - self.session_start_time).total_seconds()
                    progress = min(elapsed / 3600.0, 1.0)  # Cap at 1 hour
                    self.progress_bar.set(progress)

        except Exception as e:
            logger.error(f"Failed to update live feed: {e}")

        # Schedule next update (every 2 seconds)
        self.after(2000, self._update_live_feed)

    def _update_progress_metrics(self):
        """Update progress metrics with focus score analysis."""
        if not self.is_tracking_active or not self.ai_service:
            return

        try:
            recent_logs = self.tracker_service.get_recent_activity(limit=50)

            if recent_logs and len(recent_logs) >= 3:
                score = self.ai_service.calculate_focus_score(recent_logs, self.profile)

                if score:
                    focus_percent = min(score.value / 100.0, 1.0)
                    self.progress_bars["Focus Time"].set(focus_percent)

                    break_percent = min((1.0 - focus_percent) * 0.3, 1.0)
                    self.progress_bars["Break Time"].set(break_percent)

                    distraction_percent = max(0.0, (1.0 - focus_percent) * 0.2)
                    self.progress_bars["Distraction"].set(distraction_percent)

                    # Update summary text
                    self._update_summary_text(score)

        except Exception as e:
            logger.error(f"Failed to update progress metrics: {e}")

        # Schedule next update (every 30 seconds)
        self.after(30000, self._update_progress_metrics)

    def _update_session_time(self):
        """Update session time display."""
        if not self.is_tracking_active or not self.session_start_time:
            return

        try:
            elapsed = (datetime.now() - self.session_start_time).total_seconds()
            minutes = int(elapsed // 60)
            self.session_time.configure(text=f"Time: {minutes} min")
        except Exception as e:
            logger.error(f"Failed to update session time: {e}")

        # Schedule next update (every second)
        self.after(1000, self._update_session_time)

    def _update_progress_bar(self, label: str, value: float):
        """Update a specific progress bar."""
        if label in self.progress_bars:
            self.progress_bars[label].set(value)

    def _update_summary_text(self, score: FocusScore):
        """Update summary card with current metrics."""
        try:
            elapsed = (datetime.now() - self.session_start_time).total_seconds() if self.session_start_time else 0
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)

            summary = (
                f"{self.profile.name} has been tracking for {hours}h {minutes}m.\n"
                f"Current focus score: {int(score.value)}/100\n"
                f"Status: {score.get_label()}"
            )
            self.summary_text.configure(text=summary)
        except Exception as e:
            logger.error(f"Failed to update summary text: {e}")

    def _calculate_and_display_final_metrics(self):
        """Calculate and display final session metrics."""
        try:
            recent_logs = self.tracker_service.get_recent_activity(limit=100)

            if not recent_logs:
                return

            score = self.ai_service.calculate_focus_score(recent_logs, self.profile)

            if score:
                focus_percent = min(score.value / 100.0, 1.0)
                self.progress_bars["Focus Time"].set(focus_percent)

                break_percent = min((1.0 - focus_percent) * 0.3, 1.0)
                self.progress_bars["Break Time"].set(break_percent)

                distraction_percent = max(0.0, (1.0 - focus_percent) * 0.2)
                self.progress_bars["Distraction"].set(distraction_percent)

                logger.info(f"Final focus score: {score.value}")

        except Exception as e:
            logger.error(f"Failed to calculate final metrics: {e}")

    def cleanup(self):
        """Clean up resources when dashboard is destroyed."""
        if self.tracker_service and self.is_tracking_active:
            self.tracker_service.stop_tracking()
            self.is_tracking_active = False
            logger.info("Stopped tracking during cleanup")

    def is_tracking(self) -> bool:
        """Check if tracking is currently active."""
        return self.is_tracking_active and self.tracker_service is not None
