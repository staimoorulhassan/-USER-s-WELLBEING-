"""Notification dialogs for summaries and alerts.

Modals for displaying AI-generated summaries and other notifications.
"""

import logging
import customtkinter as ctk
from typing import Optional

from models.ai_models import DailySummary
from models.work_state import WorkState

logger = logging.getLogger(__name__)


class SummaryDialog(ctk.CTkToplevel):
    """Modal dialog for displaying daily summary."""

    def __init__(self, parent, summary: DailySummary):
        """Initialize summary dialog.

        Args:
            parent: Parent window
            summary: DailySummary to display
        """
        super().__init__(parent)

        self.summary = summary
        self._create_widgets()
        self._center_window()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Window configuration
        self.title("Daily Summary")
        self.geometry("700x600")

        # Make modal
        self.grab_set()

        # Main container
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            container,
            text="📊 Your Daily Summary",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(pady=(0, 20))

        # Scrollable content area
        scrollable = ctk.CTkScrollableFrame(container, height=400)
        scrollable.pack(fill="both", expand=True, pady=(0, 20))

        # Summary text
        self._add_section(scrollable, "Summary", self.summary.summary_text, is_main=True)

        # Productivity patterns (if available)
        if self.summary.productivity_patterns:
            patterns_text = "\n".join(f"• {pattern}" for pattern in self.summary.productivity_patterns)
            self._add_section(scrollable, "Productivity Patterns", patterns_text)

        # Time distribution (if available)
        if self.summary.time_distribution:
            dist_text = "\n".join(f"{period}: {activity}" for period, activity in self.summary.time_distribution.items())
            self._add_section(scrollable, "Time Distribution", dist_text)

        # Goal alignment (if available)
        if self.summary.goal_alignment:
            self._add_section(scrollable, "Goal Alignment", self.summary.goal_alignment)

        # Recommendations (if available)
        if self.summary.recommendations:
            recs_text = "\n".join(f"• {rec}" for rec in self.summary.recommendations)
            self._add_section(scrollable, "Recommendations", recs_text)

        # Close button
        close_button = ctk.CTkButton(
            container,
            text="Close",
            command=self.destroy,
            height=40,
            width=200,
        )
        close_button.pack(pady=(0, 10))

    def _add_section(self, parent, title: str, content: str, is_main: bool = False):
        """Add a section to the dialog.

        Args:
            parent: Parent widget
            title: Section title
            content: Section content
            is_main: Whether this is the main summary section
        """
        # Section frame
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=(0, 15))

        # Title label
        title_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=16 if is_main else 14, weight="bold"),
            anchor="w",
        )
        title_label.pack(fill="x", padx=15, pady=(15, 5))

        # Content label
        content_font_size = 14 if is_main else 12
        content_label = ctk.CTkLabel(
            section_frame,
            text=content,
            font=ctk.CTkFont(size=content_font_size),
            anchor="w",
            justify="left",
            wraplength=600,
        )
        content_label.pack(fill="x", padx=15, pady=(0, 15))

    def _center_window(self):
        """Center dialog on parent window."""
        self.update_idletasks()

        # Get parent dimensions
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()

        # Calculate position
        x = parent_x + (parent_width - self.winfo_width()) // 2
        y = parent_y + (parent_height - self.winfo_height()) // 2

        # Set position
        self.geometry(f"+{x}+{y}")


class ErrorDialog(ctk.CTkToplevel):
    """Modal dialog for displaying error messages."""

    def __init__(self, parent, title: str, message: str):
        """Initialize error dialog.

        Args:
            parent: Parent window
            title: Dialog title
            message: Error message
        """
        super().__init__(parent)

        self._create_widgets(title, message)
        self._center_window()

    def _create_widgets(self, title: str, message: str):
        """Create dialog widgets."""
        # Window configuration
        self.title(title)
        self.geometry("500x300")

        # Make modal
        self.grab_set()

        # Main container
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Icon and message
        error_label = ctk.CTkLabel(
            container,
            text="⚠️",
            font=ctk.CTkFont(size=48),
        )
        error_label.pack(pady=(20, 10))

        message_label = ctk.CTkLabel(
            container,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=400,
        )
        message_label.pack(expand=True, fill="both", pady=10)

        # Close button
        close_button = ctk.CTkButton(
            container,
            text="Close",
            command=self.destroy,
            height=40,
        )
        close_button.pack(pady=(10, 20))

    def _center_window(self):
        """Center dialog on parent window."""
        self.update_idletasks()

        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()

        x = parent_x + (parent_width - self.winfo_width()) // 2
        y = parent_y + (parent_height - self.winfo_height()) // 2

        self.geometry(f"+{x}+{y}")


class InfoDialog(ctk.CTkToplevel):
    """Modal dialog for displaying informational messages."""

    def __init__(self, parent, title: str, message: str):
        """Initialize info dialog.

        Args:
            parent: Parent window
            title: Dialog title
            message: Info message
        """
        super().__init__(parent)

        self._create_widgets(title, message)
        self._center_window()

    def _create_widgets(self, title: str, message: str):
        """Create dialog widgets."""
        self.title(title)
        self.geometry("500x250")
        self.grab_set()

        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        info_label = ctk.CTkLabel(
            container,
            text="ℹ️",
            font=ctk.CTkFont(size=48),
        )
        info_label.pack(pady=(20, 10))

        message_label = ctk.CTkLabel(
            container,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=400,
        )
        message_label.pack(expand=True, fill="both", pady=10)

        close_button = ctk.CTkButton(
            container,
            text="OK",
            command=self.destroy,
            height=40,
        )
        close_button.pack(pady=(10, 20))

    def _center_window(self):
        """Center dialog on parent window."""
        self.update_idletasks()

        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()

        x = parent_x + (parent_width - self.winfo_width()) // 2
        y = parent_y + (parent_height - self.winfo_height()) // 2

        self.geometry(f"+{x}+{y}")


class WorkStateDialog(ctk.CTkToplevel):
    """Modal dialog for displaying previous session summary on launch."""

    def __init__(self, parent, work_state: WorkState):
        """Initialize work state dialog.

        Args:
            parent: Parent window
            work_state: WorkState to display
        """
        super().__init__(parent)

        self.work_state = work_state
        self._create_widgets()
        self._center_window()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Window configuration
        self.title("Welcome Back!")
        self.geometry("600x500")

        # Make modal
        self.grab_set()

        # Main container
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title with greeting
        title_label = ctk.CTkLabel(
            container,
            text="👋 Welcome Back!",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(pady=(20, 10))

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            container,
            text="Here's a summary of your last session",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        subtitle_label.pack(pady=(0, 20))

        # Scrollable content area
        scrollable = ctk.CTkScrollableFrame(container, height=300)
        scrollable.pack(fill="both", expand=True, pady=(0, 20))

        # Session summary
        self._add_section(scrollable, "Last Session", self.work_state.session_summary)

        # Streak count (if > 0)
        if self.work_state.streak_count > 0:
            streak_text = f"{self.work_state.streak_count} consecutive productive session(s)"
            self._add_section(scrollable, "🔥 Streak", streak_text)

        # Focus score (if available)
        if self.work_state.focus_score is not None:
            score = self.work_state.focus_score
            emoji = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
            score_text = f"{emoji} {score}/100"
            self._add_section(scrollable, "Focus Score", score_text)

        # Total tracking time
        if self.work_state.total_tracking_minutes > 0:
            minutes = self.work_state.total_tracking_minutes
            hours = minutes // 60
            mins = minutes % 60
            if hours > 0:
                time_str = f"{hours}h {mins}m"
            else:
                time_str = f"{mins}m"
            self._add_section(scrollable, "Time Tracked", time_str)

        # Completed tasks (if any)
        if self.work_state.completed_tasks:
            tasks_text = "\n".join(f"• {task}" for task in self.work_state.completed_tasks)
            self._add_section(scrollable, "Completed Tasks", tasks_text)

        # Continue button
        continue_button = ctk.CTkButton(
            container,
            text="Continue",
            command=self.destroy,
            height=40,
            width=200,
            fg_color="green",
            hover_color="darkgreen",
        )
        continue_button.pack(pady=(0, 10))

    def _add_section(self, parent, title: str, content: str):
        """Add a section to the dialog.

        Args:
            parent: Parent widget
            title: Section title
            content: Section content
        """
        # Section frame
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=(0, 15))

        # Title label
        title_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        title_label.pack(fill="x", padx=15, pady=(15, 5))

        # Content label
        content_label = ctk.CTkLabel(
            section_frame,
            text=content,
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left",
            wraplength=500,
        )
        content_label.pack(fill="x", padx=15, pady=(0, 15))

    def _center_window(self):
        """Center dialog on parent window."""
        self.update_idletasks()

        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()

        x = parent_x + (parent_width - self.winfo_width()) // 2
        y = parent_y + (parent_height - self.winfo_height()) // 2

        self.geometry(f"+{x}+{y}")
