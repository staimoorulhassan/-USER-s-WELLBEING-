"""Celebration animation effects.

Provides various animation effects for task celebrations including confetti,
star bursts, and smooth transitions.
"""

import logging
import random
import time
import customtkinter as ctk
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Particle:
    """Represents a single particle in an animation."""
    x: float
    y: float
    vx: float
    vy: float
    size: float
    color: str
    life: float
    max_life: float
    shape: str = "circle"  # circle, star, square


class CelebrationEffects:
    """Manager for celebration animation effects."""

    def __init__(self, parent):
        """Initialize celebration effects.

        Args:
            parent: Parent widget (CTkFrame or similar)
        """
        self.parent = parent
        self.canvas = None
        self.active_effects: List[Dict] = []
        self.is_running = False

    def create_canvas(self, width: int = 800, height: int = 600) -> ctk.CTkCanvas:
        """Create a canvas for animations.

        Args:
            width: Canvas width
            height: Canvas height

        Returns:
            CTkCanvas widget
        """
        self.canvas = ctk.CTkCanvas(
            self.parent,
            width=width,
            height=height,
            bg="transparent",
            highlightthickness=0
        )
        return self.canvas

    def start_confetti_burst(self, x: int, y: int, count: int = 50) -> str:
        """Start a confetti burst animation.

        Args:
            x: Center x coordinate
            y: Center y coordinate
            count: Number of confetti pieces

        Returns:
            Effect ID for tracking
        """
        effect_id = f"confetti_{int(time.time() * 1000)}"
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F", "#BB8FCE"]

        confetti = []
        for i in range(count):
            particle = Particle(
                x=x + random.randint(-20, 20),
                y=y + random.randint(-20, 20),
                vx=random.uniform(-8, 8),
                vy=random.uniform(-15, -5),
                size=random.randint(3, 8),
                color=random.choice(colors),
                life=1.0,
                max_life=random.uniform(2.0, 3.0),
                shape=random.choice(["circle", "square"])
            )
            confetti.append(particle)

        effect = {
            "id": effect_id,
            "type": "confetti",
            "particles": confetti,
            "start_time": time.time()
        }

        self.active_effects.append(effect)
        if not self.is_running:
            self.is_running = True
            self._animate_effects()

        return effect_id

    def start_star_burst(self, x: int, y: int, count: int = 20) -> str:
        """Start a star burst animation.

        Args:
            x: Center x coordinate
            y: Center y coordinate
            count: Number of stars

        Returns:
            Effect ID for tracking
        """
        effect_id = f"star_{int(time.time() * 1000)}"

        stars = []
        for i in range(count):
            angle = (i / count) * 2 * 3.14159
            speed = random.uniform(5, 12)
            particle = Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                size=random.randint(15, 25),
                color="#FFD700",
                life=1.0,
                max_life=2.5,
                shape="star"
            )
            stars.append(particle)

        effect = {
            "id": effect_id,
            "type": "star_burst",
            "particles": stars,
            "start_time": time.time()
        }

        self.active_effects.append(effect)
        if not self.is_running:
            self.is_running = True
            self._animate_effects()

        return effect_id

    def start_wave_effect(self, x: int, y: int, amplitude: float = 30) -> str:
        """Start a wave ripple effect.

        Args:
            x: Center x coordinate
            y: Center y coordinate
            amplitude: Wave amplitude

        Returns:
            Effect ID for tracking
        """
        effect_id = f"wave_{int(time.time() * 1000)}"

        effect = {
            "id": effect_id,
            "type": "wave",
            "x": x,
            "y": y,
            "amplitude": amplitude,
            "frequency": 0.1,
            "phase": 0,
            "start_time": time.time(),
            "max_radius": 200,
            "current_radius": 0
        }

        self.active_effects.append(effect)
        if not self.is_running:
            self.is_running = True
            self._animate_effects()

        return effect_id

    def create_pulse_effect(self, x: int, y: int, max_radius: int = 100) -> str:
        """Create a pulse effect (single frame).

        Args:
            x: Center x coordinate
            y: Center y coordinate
            max_radius: Maximum pulse radius

        Returns:
            Effect ID for tracking
        """
        if not self.canvas:
            return ""

        effect_id = f"pulse_{int(time.time() * 1000)}"

        # Create expanding circles
        for i in range(3):
            radius = max_radius * (i + 1) / 3
            alpha = 1.0 - (i / 3)
            color = self._rgba_to_hex("#4ECDC4", alpha)

            circle_id = self.canvas.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                outline=color,
                width=3,
                fill=""
            )

            # Schedule removal
            self.parent.after(1000 + i * 200, lambda cid=circle_id: self.canvas.delete(cid))

        return effect_id

    def _animate_effects(self):
        """Animate all active effects."""
        if not self.is_running:
            return

        current_time = time.time()
        effects_to_remove = []

        for effect in self.active_effects:
            elapsed = current_time - effect["start_time"]

            if effect["type"] == "confetti":
                self._animate_confetti(effect, elapsed)
                if elapsed > 3.0:  # Effect duration
                    effects_to_remove.append(effect)

            elif effect["type"] == "star_burst":
                self._animate_star_burst(effect, elapsed)
                if elapsed > 2.5:  # Effect duration
                    effects_to_remove.append(effect)

            elif effect["type"] == "wave":
                self._animate_wave(effect, elapsed)
                if effect["current_radius"] > effect["max_radius"]:
                    effects_to_remove.append(effect)

        # Remove completed effects
        for effect in effects_to_remove:
            self.active_effects.remove(effect)

        # Continue animation if there are active effects
        if self.active_effects:
            self.parent.after(16, self._animate_effects)  # ~60 FPS
        else:
            self.is_running = False

    def _animate_confetti(self, effect: Dict, elapsed: float):
        """Animate confetti particles."""
        if not self.canvas:
            return

        particles = effect["particles"]
        dt = 0.016  # 60 FPS timestep

        for particle in particles:
            # Update physics
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            particle.vy += 300 * dt  # Gravity
            particle.life -= dt / particle.max_life

            if particle.life > 0:
                # Draw particle
                if particle.shape == "circle":
                    self.canvas.create_oval(
                        particle.x - particle.size/2,
                        particle.y - particle.size/2,
                        particle.x + particle.size/2,
                        particle.y + particle.size/2,
                        fill=particle.color,
                        outline="",
                        tags="temp"
                    )
                elif particle.shape == "square":
                    self.canvas.create_rectangle(
                        particle.x - particle.size/2,
                        particle.y - particle.size/2,
                        particle.x + particle.size/2,
                        particle.y + particle.size/2,
                        fill=particle.color,
                        outline="",
                        tags="temp"
                    )

        # Clean up old particles
        self.canvas.delete("temp")

    def _animate_star_burst(self, effect: Dict, elapsed: float):
        """Animate star burst particles."""
        if not self.canvas:
            return

        particles = effect["particles"]
        dt = 0.016  # 60 FPS timestep

        for particle in particles:
            # Update physics
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            particle.life -= dt / particle.max_life

            if particle.life > 0:
                # Draw star
                self._draw_star(
                    particle.x, particle.y,
                    particle.size, particle.life,
                    particle.color
                )

    def _animate_wave(self, effect: Dict, elapsed: float):
        """Animate wave ripple effect."""
        if not self.canvas:
            return

        effect["current_radius"] += 3  # Expand radius
        effect["phase"] += 0.2  # Update phase

        # Draw ripples
        for i in range(3):
            radius = effect["current_radius"] - i * 30
            if radius > 0:
                alpha = 1.0 - (effect["current_radius"] / effect["max_radius"])
                color = self._rgba_to_hex("#4ECDC4", alpha * (1 - i * 0.3))

                self.canvas.create_oval(
                    effect["x"] - radius, effect["y"] - radius,
                    effect["x"] + radius, effect["y"] + radius,
                    outline=color,
                    width=3,
                    tags="temp"
                )

        self.canvas.delete("temp")

    def _draw_star(self, x: float, y: float, size: float, alpha: float, color: str):
        """Draw a star shape on canvas.

        Args:
            x: Center x coordinate
            y: Center y coordinate
            size: Star size
            alpha: Transparency (0-1)
            color: Star color
        """
        # Create star polygon points
        points = []
        for i in range(10):
            angle = (i * 36 - 90) * 3.14159 / 180
            if i % 2 == 0:
                r = size
            else:
                r = size * 0.4
            px = x + r * (angle % 2) * ((-1) ** (i // 2))
            py = y + r * (angle % 2) * ((-1) ** (i // 2))
            points.extend([px, py])

        # Draw star
        adjusted_color = self._rgba_to_hex(color, alpha)
        self.canvas.create_polygon(
            points,
            fill=adjusted_color,
            outline="",
            tags="temp"
        )

    def _rgba_to_hex(self, hex_color: str, alpha: float) -> str:
        """Convert hex color with alpha to hex color with transparency effect.

        Args:
            hex_color: Hex color string (e.g., "#FF0000")
            alpha: Transparency (0-1)

        Returns:
            Hex color string with transparency effect
        """
        # Simple transparency effect - blend with background
        # In a real implementation, you'd use actual alpha blending
        if alpha < 0.5:
            return "#F0F0F0"  # Light gray for very transparent
        elif alpha < 0.8:
            return "#D0D0D0"  # Medium gray for semi-transparent
        else:
            return hex_color  # Full color

    def stop_all_effects(self):
        """Stop all active effects."""
        self.active_effects.clear()
        self.is_running = False
        if self.canvas:
            self.canvas.delete("all")

    def get_active_effects_count(self) -> int:
        """Get number of active effects.

        Returns:
            Number of active effects
        """
        return len(self.active_effects)


# Import math for calculations
import math