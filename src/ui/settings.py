"""Settings UI frame for profile management.

Allows users to view and update their profile information.
"""

import logging
import customtkinter as ctk

from models.profile import ValidationError
from services.profile_service import ProfileService

logger = logging.getLogger(__name__)


class SettingsFrame(ctk.CTkFrame):
    """Settings frame for profile management."""

    def __init__(self, parent, profile, on_save_callback=None, on_cancel_callback=None):
        """Initialize settings frame.

        Args:
            parent: Parent widget (main window)
            profile: Current UserProfile
            on_save_callback: Function to call when profile is saved
            on_cancel_callback: Function to call when changes are canceled
        """
        super().__init__(parent)

        self.parent = parent
        self.original_profile = profile
        self.profile_service = ProfileService()
        self.on_save_callback = on_save_callback
        self.on_cancel_callback = on_cancel_callback

        self._create_widgets()
        self._load_profile_data()

    def _create_widgets(self):
        """Create settings form widgets."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Settings",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title_label.grid(row=0, column=1, pady=(40, 20), sticky="ew")

        subtitle_label = ctk.CTkLabel(
            self,
            text="Update your profile information",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        subtitle_label.grid(row=1, column=1, pady=(0, 40), sticky="ew")

        # Form fields
        # Name field
        name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
        name_label.grid(row=2, column=1, pady=(10, 5), sticky="w")

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Your name")
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

        # Error message label
        self.error_label = ctk.CTkLabel(
            self, text="", text_color="red", font=ctk.CTkFont(size=12)
        )
        self.error_label.grid(row=8, column=1, pady=(10, 10), sticky="ew")

        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=9, column=1, pady=(20, 40), sticky="ew")

        # Cancel button
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            height=40,
            width=150,
            fg_color="gray",
            hover_color="darkgray",
        )
        self.cancel_button.pack(side="left", padx=(0, 10))

        # Save button
        self.save_button = ctk.CTkButton(
            button_frame,
            text="Save Changes",
            command=self._on_save,
            height=40,
            width=150,
            fg_color="green",
            hover_color="darkgreen",
        )
        self.save_button.pack(side="right")

        # Bind validation events
        self.name_entry.bind("<KeyRelease>", self._validate_form)
        self.role_entry.bind("<KeyRelease>", self._validate_form)
        self.goal_textbox.bind("<KeyRelease>", self._validate_form)

        # Initial validation
        self._validate_form()

    def _load_profile_data(self):
        """Load existing profile data into form fields."""
        self.name_entry.insert(0, self.original_profile.name)
        self.role_entry.insert(0, self.original_profile.role)
        self.goal_textbox.insert("0.0", self.original_profile.main_goal)

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

        # Basic validation (same as onboarding)
        if not name:
            self.error_label.configure(text="Name is required")
            self.save_button.configure(state="disabled")
            return

        if len(name) > 100:
            self.error_label.configure(text="Name must be 100 characters or less")
            self.save_button.configure(state="disabled")
            return

        if not role:
            self.error_label.configure(text="Role is required")
            self.save_button.configure(state="disabled")
            return

        if len(role) > 50:
            self.error_label.configure(text="Role must be 50 characters or less")
            self.save_button.configure(state="disabled")
            return

        if not goal:
            self.error_label.configure(text="Main goal is required")
            self.save_button.configure(state="disabled")
            return

        if len(goal) > 500:
            self.error_label.configure(text="Main goal must be 500 characters or less")
            self.save_button.configure(state="disabled")
            return

        # Form is valid
        self.save_button.configure(state="normal")

    def _on_save(self):
        """Handle Save Changes button click."""
        name = self.name_entry.get().strip()
        role = self.role_entry.get().strip()
        goal = self.goal_textbox.get("0.0", "end").strip()

        try:
            # Save profile updates
            updated_profile = self.profile_service.save_profile(
                name=name, role=role, main_goal=goal
            )

            logger.info(f"Profile updated for {updated_profile.name}")

            # Call save callback
            if self.on_save_callback:
                self.on_save_callback(updated_profile)

        except ValidationError as e:
            self.error_label.configure(text=str(e))
            logger.error(f"Validation error: {e}")
        except Exception as e:
            self.error_label.configure(text=f"Error: {e}")
            logger.error(f"Failed to save profile: {e}")

    def _on_cancel(self):
        """Handle Cancel button click."""
        # Revert form to original values
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, self.original_profile.name)

        self.role_entry.delete(0, "end")
        self.role_entry.insert(0, self.original_profile.role)

        self.goal_textbox.delete("0.0", "end")
        self.goal_textbox.insert("0.0", self.original_profile.main_goal)

        # Clear error
        self.error_label.configure(text="")

        # Call cancel callback
        if self.on_cancel_callback:
            self.on_cancel_callback()

        logger.info("Profile changes canceled")
