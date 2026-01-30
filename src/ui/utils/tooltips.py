"""Enhanced tooltip system for CustomTkinter widgets."""

import customtkinter as ctk


class HoverTooltip:
    """Advanced tooltip widget with fade effects and smart positioning."""

    def __init__(self, widget, text, delay=500, fade_in=True, fade_out=True):
        """Initialize tooltip.

        Args:
            widget: The widget to attach tooltip to
            text: Tooltip text content
            delay: Delay in ms before showing (500 = 0.5 seconds)
            fade_in: Enable fade-in animation
            fade_out: Enable fade-out animation
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.fade_in = fade_in
        self.fade_out = fade_out
        self.tooltip_window = None
        self.alpha = 0.0
        self.fade_steps = 10
        self.fade_step = 0

        # Bind events
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Configure>", self.on_configure)

    def on_enter(self, event=None):
        """Handle mouse enter event."""
        # Cancel any scheduled hide
        if hasattr(self, '_hide_id'):
            self.after_cancel(self._hide_id)
            del self._hide_id

        # Schedule show with delay
        self._show_id = self.widget.after(self.delay, self.show)

    def on_leave(self, event=None):
        """Handle mouse leave event."""
        # Cancel any scheduled show
        if hasattr(self, '_show_id'):
            self.widget.after_cancel(self._show_id)
            del self._show_id

        # Schedule hide
        self._hide_id = self.widget.after(100, self.hide)

    def on_configure(self, event=None):
        """Handle widget resize - reposition tooltip."""
        if self.tooltip_window and self.tooltip_window.winfo_exists():
            self.position_tooltip()

    def show(self):
        """Show the tooltip window."""
        if self.tooltip_window and self.tooltip_window.winfo_exists():
            return

        # Create tooltip window
        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_grab_set()

        # Configure transparency
        self.tooltip_window.attributes("-alpha", self.alpha)

        # Create frame with rounded corners
        frame = ctk.CTkFrame(
            self.tooltip_window,
            corner_radius=10,
            fg_color="lightgray" if ctk.get_appearance_mode() == "Light" else "gray30"
        )
        frame.pack(padx=8, pady=6)

        # Add text label
        label = ctk.CTkLabel(
            frame,
            text=self.text,
            wraplength=300,
            font=ctk.CTkFont(size=12),
            padx=10,
            pady=5
        )
        label.pack()

        # Position tooltip
        self.position_tooltip()

        # Start fade-in animation
        if self.fade_in:
            self.fade_in_step()

    def hide(self):
        """Hide the tooltip window."""
        if self.tooltip_window and self.tooltip_window.winfo_exists():
            if self.fade_out:
                self.fade_out_step()
            else:
                self.tooltip_window.destroy()
                del self.tooltip_window

    def position_tooltip(self):
        """Position tooltip relative to the widget."""
        if not self.tooltip_window:
            return

        # Get widget position
        widget_x = self.widget.winfo_rootx()
        widget_y = self.widget.winfo_rooty()
        widget_width = self.widget.winfo_width()
        widget_height = self.widget.winfo_height()

        # Get tooltip dimensions
        tooltip_width = self.tooltip_window.winfo_reqwidth()
        tooltip_height = self.tooltip_window.winfo_reqheight()

        # Calculate position (above the widget)
        x = widget_x + (widget_width - tooltip_width) // 2
        y = widget_y - tooltip_height - 10  # 10 pixels above widget

        # Adjust if tooltip would go off-screen
        screen_width = self.tooltip_window.winfo_screenwidth()
        screen_height = self.tooltip_window.winfo_screenheight()

        if x < 10:
            x = 10
        elif x + tooltip_width > screen_width - 10:
            x = screen_width - tooltip_width - 10

        if y < 10:
            # If tooltip would go off top, position below widget
            y = widget_y + widget_height + 10

        # Position the window
        self.tooltip_window.geometry(f"+{x}+{y}")

    def fade_in_step(self):
        """Perform one step of fade-in animation."""
        if self.tooltip_window and self.tooltip_window.winfo_exists():
            if self.alpha < 1.0:
                self.alpha += 0.1
                self.tooltip_window.attributes("-alpha", self.alpha)
                self.tooltip_window.after(30, self.fade_in_step)
            else:
                self.alpha = 1.0
                self.tooltip_window.attributes("-alpha", self.alpha)

    def fade_out_step(self):
        """Perform one step of fade-out animation."""
        if self.tooltip_window and self.tooltip_window.winfo_exists():
            if self.alpha > 0.0:
                self.alpha -= 0.1
                self.tooltip_window.attributes("-alpha", self.alpha)
                self.tooltip_window.after(30, self.fade_out_step)
            else:
                self.tooltip_window.destroy()
                del self.tooltip_window

    def destroy(self):
        """Clean up tooltip resources."""
        # Cancel any pending operations
        for attr in ['_show_id', '_hide_id']:
            if hasattr(self, attr):
                self.widget.after_cancel(getattr(self, attr))
                delattr(self, attr)

        # Hide tooltip if showing
        if hasattr(self, 'tooltip_window') and self.tooltip_window and self.tooltip_window.winfo_exists():
            self.tooltip_window.destroy()

        # Unbind events
        self.widget.unbind("<Enter>")
        self.widget.unbind("<Leave>")
        self.widget.unbind("<Configure>")


def add_tooltip(widget, text, tooltip_type="standard"):
    """Add a tooltip to a widget with predefined configurations.

    Args:
        widget: The widget to add tooltip to
        text: Tooltip text
        tooltip_type: Predefined style ("standard", "help", "warning")
    """
    # Customize based on type
    if tooltip_type == "help":
        delay = 300  # Show faster for help tooltips
        text = f"ℹ️ {text}"
    elif tooltip_type == "warning":
        delay = 400
        text = f"⚠️ {text}"
    else:  # standard
        delay = 500

    return HoverTooltip(widget, text, delay=delay)


# Predefined tooltip configurations
TOOLTIP_TEXTS = {
    "start_tracking": "Begin monitoring your active windows",
    "stop_tracking": "Pause activity tracking",
    "stop_summarize": "Generate AI-powered daily summary",
    "focus_score": "AI-calculated productivity metric (0-100)",
    "live_feed": "Real-time window activity log",
    "settings": "Manage your profile and preferences",
    "create_profile": "Set up your account with basic information",
    "save_profile": "Save your profile settings",
    "start_session": "Begin a new work session",
    "pause_session": "Pause tracking temporarily"
}


def add_default_tooltip(widget, action_key):
    """Add a tooltip with predefined text based on action key.

    Args:
        widget: The widget to add tooltip to
        action_key: Key from TOOLTIP_TEXTS dictionary
    """
    if action_key in TOOLTIP_TEXTS:
        return add_tooltip(widget, TOOLTIP_TEXTS[action_key])
    else:
        return add_tooltip(widget, action_key)