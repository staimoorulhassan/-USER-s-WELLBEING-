"""Celebration settings dialog.

Configure celebration preferences including sound, animations, and detection settings.
"""

import logging
import customtkinter as ctk
from typing import Optional

from services.task_detection import TaskDetectionService

logger = logging.getLogger(__name__)


class CelebrationSettingsDialog(ctk.CTkToplevel):
    """Dialog for configuring celebration settings."""

    def __init__(self, parent, task_detection_service: Optional[TaskDetectionService] = None):
        """Initialize celebration settings dialog.

        Args:
            parent: Parent window
            task_detection_service: Task detection service to configure
        """
        super().__init__(parent)

        self.task_detection_service = task_detection_service
        self.settings = {
            "celebrations_enabled": True,
            "animations_enabled": True,
            "sound_enabled": False,
            "popup_frequency": "normal",
            "popup_animation": "star_flash",
            "confidence_threshold": 0.7,
            "cooldown_period": 300,
            "window_size": 10
        }

        self._create_widgets()
        self._center_window()

        # Make modal
        self.grab_set()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Window configuration
        self.title("Celebration Settings")
        self.geometry("600x700")

        # Main container
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_container,
            text="🎉 Celebration Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(pady=(0, 30))

        # General Settings
        general_frame = ctk.CTkFrame(main_container)
        general_frame.pack(fill="x", padx=10, pady=(0, 20))

        general_title = ctk.CTkLabel(
            general_frame,
            text="General Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        general_title.pack(pady=(10, 10))

        # Celebrations enabled
        self.celebrations_var = ctk.BooleanVar(value=self.settings["celebrations_enabled"])
        celebrations_check = ctk.CTkCheckBox(
            general_frame,
            text="Enable Celebrations",
            variable=self.celebrations_var,
            command=self._on_celebrations_changed
        )
        celebrations_check.pack(pady=5)

        # Animations enabled
        self.animations_var = ctk.BooleanVar(value=self.settings["animations_enabled"])
        animations_check = ctk.CTkCheckBox(
            general_frame,
            text="Enable Animations",
            variable=self.animations_var,
        )
        animations_check.pack(pady=5)

        # Sound enabled
        self.sound_var = ctk.BooleanVar(value=self.settings["sound_enabled"])
        sound_check = ctk.CTkCheckBox(
            general_frame,
            text="Enable Sound Effects",
            variable=self.sound_var,
        )
        sound_check.pack(pady=5)

        # Detection Settings
        detection_frame = ctk.CTkFrame(main_container)
        detection_frame.pack(fill="x", padx=10, pady=(0, 20))

        detection_title = ctk.CTkLabel(
            detection_frame,
            text="Detection Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        detection_title.pack(pady=(10, 10))

        # Confidence threshold
        threshold_frame = ctk.CTkFrame(detection_frame)
        threshold_frame.pack(fill="x", padx=10, pady=5)

        threshold_label = ctk.CTkLabel(
            threshold_frame,
            text="Confidence Threshold:",
            font=ctk.CTkFont(size=14),
        )
        threshold_label.pack(side="left", padx=10, pady=5)

        self.threshold_var = ctk.DoubleVar(value=self.settings["confidence_threshold"])
        threshold_slider = ctk.CTkSlider(
            threshold_frame,
            from_=0.5,
            to=1.0,
            variable=self.threshold_var,
            number_of_steps=10,
            command=self._on_threshold_changed
        )
        threshold_slider.pack(side="left", fill="x", expand=True, padx=10, pady=5)

        self.threshold_label = ctk.CTkLabel(
            threshold_frame,
            text=f"{self.settings['confidence_threshold']:.1f}",
            font=ctk.CTkFont(size=12),
            width=40
        )
        self.threshold_label.pack(side="right", padx=10, pady=5)

        # Activity window size
        window_frame = ctk.CTkFrame(detection_frame)
        window_frame.pack(fill="x", padx=10, pady=5)

        window_label = ctk.CTkLabel(
            window_frame,
            text="Activity Window (minutes):",
            font=ctk.CTkFont(size=14),
        )
        window_label.pack(side="left", padx=10, pady=5)

        self.window_var = ctk.IntVar(value=self.settings["window_size"])
        window_spinbox = ctk.CTkSpinBox(
            window_frame,
            from_=5,
            to=30,
            variable=self.window_var,
            width=60,
            command=self._on_window_size_changed
        )
        window_spinbox.pack(side="left", padx=10, pady=5)

        # Cooldown period
        cooldown_frame = ctk.CTkFrame(detection_frame)
        cooldown_frame.pack(fill="x", padx=10, pady=5)

        cooldown_label = ctk.CTkLabel(
            cooldown_frame,
            text="Cooldown Period (seconds):",
            font=ctk.CTkFont(size=14),
        )
        cooldown_label.pack(side="left", padx=10, pady=5)

        self.cooldown_var = ctk.IntVar(value=self.settings["cooldown_period"])
        cooldown_spinbox = ctk.CTkSpinBox(
            cooldown_frame,
            from_=60,
            to=600,
            increment=60,
            variable=self.cooldown_var,
            width=80,
            command=self._on_cooldown_changed
        )
        cooldown_spinbox.pack(side="left", padx=10, pady=5)

        # Popup Settings
        popup_frame = ctk.CTkFrame(main_container)
        popup_frame.pack(fill="x", padx=10, pady=(0, 20))

        popup_title = ctk.CTkLabel(
            popup_frame,
            text="Popup Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        popup_title.pack(pady=(10, 10))

        # Popup frequency
        freq_frame = ctk.CTkFrame(popup_frame)
        freq_frame.pack(fill="x", padx=10, pady=5)

        freq_label = ctk.CTkLabel(
            freq_frame,
            text="Popup Frequency:",
            font=ctk.CTkFont(size=14),
        )
        freq_label.pack(side="left", padx=10, pady=5)

        self.freq_var = ctk.StringVar(value=self.settings["popup_frequency"])
        freq_combo = ctk.CTkComboBox(
            freq_frame,
            variable=self.freq_var,
            values=["low", "normal", "high"],
            width=120,
            state="readonly"
        )
        freq_combo.pack(side="left", padx=10, pady=5)

        # Popup animation
        anim_frame = ctk.CTkFrame(popup_frame)
        anim_frame.pack(fill="x", padx=10, pady=5)

        anim_label = ctk.CTkLabel(
            anim_frame,
            text="Popup Animation:",
            font=ctk.CTkFont(size=14),
        )
        anim_label.pack(side="left", padx=10, pady=5)

        self.anim_var = ctk.StringVar(value=self.settings["popup_animation"])
        anim_combo = ctk.CTkComboBox(
            anim_frame,
            variable=self.anim_var,
            values=["star_flash", "confetti", "wave"],
            width=120,
            state="readonly"
        )
        anim_combo.pack(side="left", padx=10, pady=5)

        # Buttons
        button_frame = ctk.CTkFrame(main_container)
        button_frame.pack(fill="x", pady=(20, 10))

        # Save button
        save_button = ctk.CTkButton(
            button_frame,
            text="Save Settings",
            command=self._save_settings,
            width=150,
            height=40
        )
        save_button.pack(side="left", padx=10, pady=10)

        # Cancel button
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=150,
            height=40
        )
        cancel_button.pack(side="right", padx=10, pady=10)

    def _center_window(self):
        """Center the dialog on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()

        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")

    def _on_celebrations_changed(self):
        """Handle celebrations enabled/disabled change."""
        self.settings["celebrations_enabled"] = self.celebrations_var.get()

        # Update detection service if available
        if self.task_detection_service and self.settings["celebrations_enabled"]:
            self.task_detection_service.start_detection()
        elif self.task_detection_service and not self.settings["celebrations_enabled"]:
            self.task_detection_service.stop_detection()

    def _on_threshold_changed(self, value):
        """Handle confidence threshold change."""
        self.settings["confidence_threshold"] = float(value)
        self.threshold_label.configure(text=f"{float(value):.1f}")

        # Update detection service
        if self.task_detection_service:
            self.task_detection_service.set_detection_parameters(
                window_size_minutes=self.settings["window_size"],
                min_confidence=self.settings["confidence_threshold"],
                cooldown_period=self.settings["cooldown_period"]
            )

    def _on_window_size_changed(self, value):
        """Handle activity window size change."""
        self.settings["window_size"] = int(value)

        # Update detection service
        if self.task_detection_service:
            self.task_detection_service.set_detection_parameters(
                window_size_minutes=self.settings["window_size"],
                min_confidence=self.settings["confidence_threshold"],
                cooldown_period=self.settings["cooldown_period"]
            )

    def _on_cooldown_changed(self, value):
        """Handle cooldown period change."""
        self.settings["cooldown_period"] = int(value)

        # Update detection service
        if self.task_detection_service:
            self.task_detection_service.set_detection_parameters(
                window_size_minutes=self.settings["window_size"],
                min_confidence=self.settings["confidence_threshold"],
                cooldown_period=self.settings["cooldown_period"]
            )

    def _save_settings(self):
        """Save settings and close dialog."""
        # Update all settings
        self.settings.update({
            "celebrations_enabled": self.celebrations_var.get(),
            "animations_enabled": self.animations_var.get(),
            "sound_enabled": self.sound_var.get(),
            "popup_frequency": self.freq_var.get(),
            "popup_animation": self.anim_var.get(),
            "confidence_threshold": self.threshold_var.get(),
            "cooldown_period": self.cooldown_var.get(),
            "window_size": self.window_var.get()
        })

        # Apply settings to detection service
        if self.task_detection_service:
            self.task_detection_service.set_detection_parameters(
                window_size_minutes=self.settings["window_size"],
                min_confidence=self.settings["confidence_threshold"],
                cooldown_period=self.settings["cooldown_period"]
            )

            # Start/stop detection based on celebrations enabled
            if self.settings["celebrations_enabled"]:
                self.task_detection_service.start_detection()
            else:
                self.task_detection_service.stop_detection()

        logger.info("Celebration settings saved")
        self.destroy()

    def get_settings(self) -> dict:
        """Get current settings.

        Returns:
            Dictionary with current settings
        """
        return self.settings.copy()


# Global instance for settings persistence
_celebration_settings = {}


def get_celebration_settings() -> dict:
    """Get celebration settings with defaults."""
    global _celebration_settings

    if not _celebration_settings:
        _celebration_settings = {
            "celebrations_enabled": True,
            "animations_enabled": True,
            "sound_enabled": False,
            "popup_frequency": "normal",
            "popup_animation": "star_flash",
            "confidence_threshold": 0.7,
            "cooldown_period": 300,
            "window_size": 10
        }

    return _celebration_settings


def save_celebration_settings(settings: dict) -> None:
    """Save celebration settings.

    Args:
        settings: Settings dictionary to save
    """
    global _celebration_settings
    _celebration_settings = settings.copy()