"""3D visual effects utilities for enhanced UI appearance."""

import customtkinter as ctk


class GradientFrame(ctk.CTkFrame):
    """Frame with gradient background effect."""

    def __init__(self, master, color1=None, color2=None, **kwargs):
        """Initialize gradient frame.

        Args:
            master: Parent widget
            color1: Top color (lighter)
            color2: Bottom color (darker)
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(master, **kwargs)

        # Default gradient colors
        self.color1 = color1 or ("#F0F0F0" if ctk.get_appearance_mode() == "Light" else "#404040")
        self.color2 = color2 or ("#E0E0E0" if ctk.get_appearance_mode() == "Light" else "#303030")

        self.gradient_canvas = None
        self._setup_gradient()

    def _setup_gradient(self):
        """Setup gradient background canvas."""
        # Create canvas that covers the entire frame
        self.gradient_canvas = ctk.CTkCanvas(
            self,
            highlightthickness=0
        )
        self.gradient_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Create gradient
        self._draw_gradient()

    def _draw_gradient(self):
        """Draw gradient on canvas."""
        if not self.gradient_canvas:
            return

        # Get canvas dimensions
        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 1 or height <= 1:
            # Canvas not ready yet, schedule redraw
            self.after(100, self._draw_gradient)
            return

        # Create gradient segments
        steps = 20
        for i in range(steps):
            y1 = (i * height) // steps
            y2 = ((i + 1) * height) // steps

            # Interpolate color
            ratio = i / (steps - 1)
            color = self._interpolate_color(self.color1, self.color2, ratio)

            # Draw segment
            self.gradient_canvas.create_rectangle(
                0, y1, width, y2,
                fill=color,
                outline=""
            )

    def _interpolate_color(self, color1, color2, ratio):
        """Interpolate between two hex colors."""
        # Convert hex to RGB
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)

        # Interpolate
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def update_appearance(self):
        """Update gradient when appearance mode changes."""
        self.color1 = ("#F0F0F0" if ctk.get_appearance_mode() == "Light" else "#404040")
        self.color2 = ("#E0E0E0" if ctk.get_appearance_mode() == "Light" else "#303030")
        self._draw_gradient()

    def configure(self, **kwargs):
        """Override configure to handle gradient updates."""
        if "fg_color" in kwargs:
            # Don't set background for gradient frame
            kwargs.pop("fg_color", None)
        super().configure(**kwargs)
        self._draw_gradient()


class RoundedRectangleFrame(ctk.CTkFrame):
    """Frame with rounded corners for 3D effect."""

    def __init__(self, master, corner_radius=15, **kwargs):
        """Initialize rounded rectangle frame.

        Args:
            master: Parent widget
            corner_radius: Radius of corners (pixels)
            **kwargs: Additional CTkFrame arguments
        """
        self.corner_radius = corner_radius
        super().__init__(master, **kwargs)

        # Hide default background
        self.configure(fg_color="transparent")

        # Create canvas for drawing
        self.canvas = ctk.CTkCanvas(
            self,
            highlightthickness=0,
            bg="transparent"
        )
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Draw initial shape
        self._draw_background()

    def _draw_background(self):
        """Draw rounded rectangle background."""
        if not self.canvas:
            return

        # Get dimensions
        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 1 or height <= 1:
            # Not ready yet
            self.after(100, self._draw_background)
            return

        # Clear canvas
        self.canvas.delete("all")

        # Get frame's bg_color
        bg_color = self.cget("fg_color") or self.cget("bg_color")

        if bg_color and bg_color != "transparent":
            # Draw rounded rectangle
            self.canvas.create_rectangle(
                self.corner_radius, 0,
                width - self.corner_radius, height,
                fill=bg_color,
                outline="",
                tags="bg"
            )

            # Draw rounded corners
            # Top-left
            self.canvas.create_arc(
                0, 0, self.corner_radius * 2, self.corner_radius * 2,
                start=90, extent=90,
                fill=bg_color,
                outline="",
                tags="bg"
            )

            # Top-right
            self.canvas.create_arc(
                width - self.corner_radius * 2, 0,
                width, self.corner_radius * 2,
                start=0, extent=90,
                fill=bg_color,
                outline="",
                tags="bg"
            )

            # Bottom-left
            self.canvas.create_arc(
                0, height - self.corner_radius * 2,
                self.corner_radius * 2, height,
                start=180, extent=90,
                fill=bg_color,
                outline="",
                tags="bg"
            )

            # Bottom-right
            self.canvas.create_arc(
                width - self.corner_radius * 2, height - self.corner_radius * 2,
                width, height,
                start=270, extent=90,
                fill=bg_color,
                outline="",
                tags="bg"
            )

    def configure(self, **kwargs):
        """Override configure to redraw when appearance changes."""
        if "fg_color" in kwargs or "bg_color" in kwargs:
            # Schedule redraw
            self.after(100, self._draw_background)
        super().configure(**kwargs)


class ShadowButton(ctk.CTkButton):
    """Button with 3D shadow and enhanced hover effects."""

    def __init__(self, master, shadow_color="gray20", shadow_offset=2, **kwargs):
        """Initialize shadow button.

        Args:
            master: Parent widget
            shadow_color: Color of the shadow
            shadow_offset: Offset of shadow from button
            **kwargs: Additional CTkButton arguments
        """
        self.shadow_color = shadow_color
        self.shadow_offset = shadow_offset

        # Set default hover colors if not specified
        if "hover_color" not in kwargs:
            fg_color = kwargs.get("fg_color", "blue")
            kwargs["hover_color"] = self._darken_color(fg_color, 0.2)

        super().__init__(master, **kwargs)

        # Create shadow canvas
        self.shadow_canvas = ctk.CTkCanvas(
            self,
            highlightthickness=0,
            bg="transparent"
        )
        self.shadow_canvas.place(x=self.shadow_offset, y=self.shadow_offset, relwidth=1, relheight=1)

        # Update shadow when hovered
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _darken_color(self, color, factor):
        """Darken a color by a factor."""
        if color.startswith("#"):
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            r = int(r * (1 - factor))
            g = int(g * (1 - factor))
            b = int(b * (1 - factor))
            return f"#{r:02x}{g:02x}{b:02x}"
        return color

    def _on_enter(self, event):
        """Handle mouse enter - bring button to front."""
        self.lower(self.shadow_canvas)

    def _on_leave(self, event):
        """Handle mouse leave - push shadow back."""
        self.shadow_canvas.place(x=self.shadow_offset, y=self.shadow_offset, relwidth=1, relheight=1)


def apply_3d_style(widget, widget_type="frame"):
    """Apply consistent 3D styling to a widget.

    Args:
        widget: The widget to style
        widget_type: Type of widget ("frame", "button", "card")
    """
    if widget_type == "frame":
        widget.configure(corner_radius=10)
    elif widget_type == "button":
        widget.configure(height=40, corner_radius=8, font=ctk.CTkFont(size=14, weight="bold"))
    elif widget_type == "card":
        widget.configure(corner_radius=15)


class FocusScoreCard(GradientFrame):
    """Special gradient card for focus score with color-based gradients."""

    def __init__(self, master, score=0, **kwargs):
        """Initialize focus score card.

        Args:
            master: Parent widget
            score: Current focus score (0-100)
            **kwargs: Additional arguments
        """
        self.score = score
        super().__init__(master, color1="#FFFFFF", color2="#FFFFFF", **kwargs)
        self._update_gradient()

    def _update_gradient(self):
        """Update gradient based on focus score."""
        # Color mapping based on score
        if self.score >= 70:
            # Green gradient
            self.color1 = "#E8F5E9"
            self.color2 = "#C8E6C9"
        elif self.score >= 50:
            # Yellow gradient
            self.color1 = "#FFF8E1"
            self.color2 = "#FFECB3"
        elif self.score >= 30:
            # Orange gradient
            self.color1 = "#FFF3E0"
            self.color2 = "#FFE0B2"
        else:
            # Red gradient
            self.color1 = "#FFEBEE"
            self.color2 = "#FFCDD2"

        self._draw_gradient()

    def set_score(self, score):
        """Update the focus score and refresh gradient."""
        self.score = max(0, min(100, score))
        self._update_gradient()