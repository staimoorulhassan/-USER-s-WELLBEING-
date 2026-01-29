"""Onboarding UI frame for first-time user setup.

Collects user's name, role, and main goal through a form.
"""

import logging
import customtkinter as ctk

from models.profile import ValidationError
from services.profile_service import ProfileService

logger = logging.getLogger(__name__)


class OnboardingFrame(ctk.CTkFrame):
    """Onboarding form frame for user profile setup."""

    def __init__(self, parent, on_complete_callback):
        """Initialize onboarding frame.

        Args:
            parent: Parent widget (main window)
            on_complete_callback: Function to call when onboarding completes
        """
        super().__init__(parent)

        self.parent = parent
        self.on_complete_callback = on_complete_callback
        self.profile_service = ProfileService()

        self._create_widgets()

    def _create_widgets(self):
        """Create onboarding form widgets."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Welcome to Wellbeing!",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title_label.grid(row=0, column=1, pady=(40, 20), sticky="ew")

        subtitle_label = ctk.CTkLabel(
            self,
            text="Let's set up your profile to get started",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        subtitle_label.grid(row=1, column=1, pady=(0, 40), sticky="ew")

        # Form fields
        # Name field
        name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
        name_label.grid(row=2, column=1, pady=(10, 5), sticky="w")

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Enter your name")
        self.name_entry.grid(row=3, column=1, pady=(0, 20), sticky="ew")

        # Role field
        role_label = ctk.CTkLabel(self, text="Role:", anchor="w")
        role_label.grid(row=4, column=1, pady=(10, 5), sticky="w")

        self.role_entry = ctk.CTkEntry(self, placeholder_text="e.g., Developer, Designer, Manager")
        self.role_entry.grid(row=5, column=1, pady=(0, 20), sticky="ew")

        # Main goal field
        goal_label = ctk.CTkLabel(self, text="Main Goal:", anchor="w")
        goal_label.grid(row=6, column=1, pady=(10, 5), sticky="w")

        self.goal_textbox = ctk.CTkTextbox(self, height=100)
        self.goal_textbox.grid(row=7, column=1, pady=(0, 10), sticky="ew")
        self.goal_textbox.insert("0.0", "What would you like to accomplish?")

        # Error message label
        self.error_label = ctk.CTkLabel(
            self, text="", text_color="red", font=ctk.CTkFont(size=12)
        )
        self.error_label.grid(row=8, column=1, pady=(10, 10), sticky="ew")

        # Submit button
        self.submit_button = ctk.CTkButton(
            self,
            text="Start Tracking",
            command=self._on_submit,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.submit_button.grid(row=9, column=1, pady=(20, 40), sticky="ew")

        # Bind validation events
        self.name_entry.bind("<KeyRelease>", self._validate_form)
        self.role_entry.bind("<KeyRelease>", self._validate_form)
        self.goal_textbox.bind("<KeyRelease>", self._validate_form)

        # Initial validation
        self._validate_form()

    def _validate_form(self, event=None):
        """Validate form and update error message.

        Args:
            event: Key event (optional)
        """
        name = self.name_entry.get().strip()
        role = self.role_entry.get().strip()
        goal = self.goal_textbox.get("0.0", "end").strip()

        # Clear error
        self.error_label.configure(text="")

        # Basic validation
        if not name:
            self.error_label.configure(text="Name is required")
            self.submit_button.configure(state="disabled")
            return

        if len(name) > 100:
            self.error_label.configure(text="Name must be 100 characters or less")
            self.submit_button.configure(state="disabled")
            return

        if not role:
            self.error_label.configure(text="Role is required")
            self.submit_button.configure(state="disabled")
            return

        if len(role) > 50:
            self.error_label.configure(text="Role must be 50 characters or less")
            self.submit_button.configure(state="disabled")
            return

        if not goal or goal == "What would you like to accomplish?":
            self.error_label.configure(text="Main goal is required")
            self.submit_button.configure(state="disabled")
            return

        if len(goal) > 500:
            self.error_label.configure(text="Main goal must be 500 characters or less")
            self.submit_button.configure(state="disabled")
            return

        # Form is valid
        self.submit_button.configure(state="normal")

    def _on_submit(self):
        """Handle form submission."""
        name = self.name_entry.get().strip()
        role = self.role_entry.get().strip()
        goal = self.goal_textbox.get("0.0", "end").strip()

        try:
            # Save profile
            profile = self.profile_service.save_profile(
                name=name, role=role, main_goal=goal
            )

            logger.info(f"Onboarding completed for {profile.name}")

            # Call completion callback
            if self.on_complete_callback:
                self.on_complete_callback(profile)

        except ValidationError as e:
            self.error_label.configure(text=str(e))
            logger.error(f"Validation error: {e}")
        except Exception as e:
            self.error_label.configure(text=f"Error: {e}")
            logger.error(f"Failed to save profile: {e}")
