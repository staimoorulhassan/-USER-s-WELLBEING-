"""Celebration popup notifications for task accomplishments.

Shows animated star flash notifications when tasks are completed.
"""

import logging
import threading
import time
import customtkinter as ctk
from typing import Optional, List, Callable
from datetime import datetime, timedelta

from models.activity_log import ActivityLogEntry
from services.task_detection import TaskAccomplishment

logger = logging.getLogger(__name__)


class StarFlashPopup(ctk.CTkToplevel):
    """Animated star flash popup for task celebrations."""

    def __init__(self, parent, accomplishment: TaskAccomplishment, on_close: Optional[Callable] = None):
        """Initialize star flash popup.

        Args:
            parent: Parent window
            accomplishment: Task accomplishment to celebrate
            on_close: Callback when popup closes
        """
        super().__init__(parent)

        self.accomplishment = accomplishment
        self.on_close = on_close
        self.animation_frame = 0
        self.max_frames = 30
        self.stars = []
        self.is_animating = True

        # Window configuration
        self.title("Task Accomplished!")
        self.geometry("400x300")
        self.attributes("-topmost", True)  # Always on top
        self.overrideredirect(True)  # No window decorations

        # Create widgets
        self._create_widgets()

        # Center the popup
        self._center_window()

        # Start animation
        self._animate()

    def _create_widgets(self):
        """Create popup widgets."""
        # Main container
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        self.title_label = ctk.CTkLabel(
            self.container,
            text="🎉 Task Accomplished!",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#FFD700"
        )
        self.title_label.pack(pady=(0, 20))

        # Task name
        self.task_label = ctk.CTkLabel(
            self.container,
            text=f"Completed: {self.accomplishment.task_name}",
            font=ctk.CTkFont(size=18),
            wraplength=350,
            justify="center"
        )
        self.task_label.pack(pady=(0, 10))

        # Confidence indicator
        confidence_color = self._get_confidence_color(self.accomplishment.confidence)
        self.confidence_label = ctk.CTkLabel(
            self.container,
            text=f"Confidence: {self.accomplishment.confidence:.0%}",
            font=ctk.CTkFont(size=14),
            text_color=confidence_color
        )
        self.confidence_label.pack(pady=(0, 20))

        # Canvas for star animations
        self.canvas = ctk.CTkCanvas(
            self.container,
            width=350,
            height=100,
            bg="transparent"
        )
        self.canvas.pack(pady=(0, 20))

        # Create initial stars
        self._create_stars()

        # Context info
        if self.accomplishment.context:
            context_label = ctk.CTkLabel(
                self.container,
                text=self.accomplishment.context,
                font=ctk.CTkFont(size=12),
                text_color="gray",
                wraplength=350,
                justify="center"
            )
            context_label.pack()

    def _get_confidence_color(self, confidence: float) -> str:
        """Get color based on confidence level.

        Args:
            confidence: Confidence score (0-1)

        Returns:
            Color string for confidence label
        """
        if confidence >= 0.9:
            return "#00FF00"  # Green - very confident
        elif confidence >= 0.8:
            return "#90EE90"  # Light green - confident
        elif confidence >= 0.7:
            return "#FFD700"  # Gold - moderate confidence
        else:
            return "#FFA500"  # Orange - low confidence

    def _create_stars(self):
        """Create star objects on canvas."""
        self.stars = []
        for i in range(5):
            x = 50 + i * 60
            y = 50
            size = 20
            star = self.canvas.create_polygon(
                self._star_coords(x, y, size),
                fill="#FFD700",
                outline="#FFA500",
                width=2
            )
            self.stars.append({
                "id": star,
                "x": x,
                "y": y,
                "size": size,
                "vx": (i - 2) * 2,  # Velocity based on position
                "vy": -3,
                "rotation": 0
            })

    def _star_coords(self, x: float, y: float, size: float) -> List[float]:
        """Generate star polygon coordinates.

        Args:
            x: Center x coordinate
            y: Center y coordinate
            size: Star size

        Returns:
            List of coordinates for star polygon
        """
        coords = []
        for i in range(10):
            angle = (i * 36 - 90) * 3.14159 / 180
            if i % 2 == 0:
                r = size
            else:
                r = size * 0.4
            coord_x = x + r * (angle % 2) * ((-1) ** (i // 2))
            coord_y = y + r * (angle % 2) * ((-1) ** (i // 2))
            coords.extend([coord_x, coord_y])
        return coords

    def _animate(self):
        """Animate the popup."""
        if not self.is_animating:
            return

        self.animation_frame += 1

        # Animate stars
        for star in self.stars:
            # Update position
            star["x"] += star["vx"]
            star["y"] += star["vy"]
            star["vy"] += 0.5  # Gravity
            star["rotation"] += 5

            # Update star on canvas
            self.canvas.delete(star["id"])
            new_coords = self._rotated_star_coords(
                star["x"], star["y"], star["size"], star["rotation"]
            )
            star["id"] = self.canvas.create_polygon(
                new_coords,
                fill="#FFD700",
                outline="#FFA500",
                width=2
            )

        # Fade out effect
        if self.animation_frame > self.max_frames - 10:
            alpha = (self.max_frames - self.animation_frame) / 10
            self.canvas.configure(bg=f"#{int(255*alpha):02x}{int(255*alpha):02x}{int(255*alpha):02x}")

        # Check if animation should end
        if self.animation_frame >= self.max_frames:
            self._close_popup()
            return

        # Schedule next frame
        self.after(50, self._animate)

    def _rotated_star_coords(self, x: float, y: float, size: float, rotation: float) -> List[float]:
        """Generate rotated star polygon coordinates.

        Args:
            x: Center x coordinate
            y: Center y coordinate
            size: Star size
            rotation: Rotation angle in degrees

        Returns:
            List of coordinates for rotated star polygon
        """
        coords = []
        rad = rotation * 3.14159 / 180

        for i in range(10):
            angle = (i * 36 - 90) * 3.14159 / 180 + rad
            if i % 2 == 0:
                r = size
            else:
                r = size * 0.4
            coord_x = x + r * (angle % 2) * ((-1) ** (i // 2))
            coord_y = y + r * (angle % 2) * ((-1) ** (i // 2))
            coords.extend([coord_x, coord_y])
        return coords

    def _center_window(self):
        """Center the popup on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()

        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")

    def _close_popup(self):
        """Close the popup."""
        self.is_animating = False
        if self.on_close:
            self.on_close()
        self.destroy()

    def destroy(self):
        """Destroy the popup and cleanup."""
        self.is_animating = False
        super().destroy()


class CelebrationManager:
    """Manager for celebration popups and animations."""

    def __init__(self, parent_window):
        """Initialize celebration manager.

        Args:
            parent_window: Main application window
        """
        self.parent_window = parent_window
        self.active_popups: List[StarFlashPopup] = []
        self.max_concurrent_popups = 3
        self.min_popup_interval = 2000  # milliseconds
        self.last_popup_time = 0

    def show_celebration(self, accomplishment: TaskAccomplishment):
        """Show celebration popup for task accomplishment.

        Args:
            accomplishment: Task accomplishment to celebrate
        """
        # Check if we can show a new popup
        current_time = time.time() * 1000
        if (current_time - self.last_popup_time) < self.min_popup_interval:
            return

        # Check max concurrent popups
        if len(self.active_popups) >= self.max_concurrent_popups:
            return

        # Create and show popup
        def on_close():
            """Handle popup close."""
            if popup in self.active_popups:
                self.active_popups.remove(popup)

        popup = StarFlashPopup(self.parent_window, accomplishment, on_close)
        self.active_popups.append(popup)
        self.last_popup_time = current_time

        # Make sure popup is destroyed on parent close
        def cleanup():
            if popup.winfo_exists():
                popup.destroy()

        self.parent_window.protocol("WM_DELETE_WINDOW", cleanup)

    def cleanup_all(self):
        """Clean up all active popups."""
        for popup in self.active_popups[:]:
            if popup.winfo_exists():
                popup.destroy()
        self.active_popups.clear()

    def set_popup_config(self, max_concurrent: int = 3, min_interval: int = 2000):
        """Configure popup behavior.

        Args:
            max_concurrent: Maximum concurrent popups
            min_interval: Minimum milliseconds between popups
        """
        self.max_concurrent_popups = max_concurrent
        self.min_popup_interval = min_interval


# Factory function for easy creation
def create_celebration_popup(parent, accomplishment: TaskAccomplishment) -> StarFlashPopup:
    """Create a celebration popup.

    Args:
        parent: Parent window
        accomplishment: Task accomplishment to celebrate

    Returns:
        StarFlashPopup instance
    """
    return StarFlashPopup(parent, accomplishment)