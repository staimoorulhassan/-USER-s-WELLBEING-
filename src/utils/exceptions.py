"""Wellbeing application exception hierarchy."""

from typing import Optional


class WellbeingError(Exception):
    """Base exception for all Wellbeing application errors."""

    def __init__(self, message: str, details: Optional[str] = None):
        """Initialize exception with message and optional details.

        Args:
            message: Human-readable error message
            details: Additional technical details
        """
        self.message = message
        self.details = details
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format full error message with details if present."""
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class TrackerError(WellbeingError):
    """Raised when tracking service operations fail."""

    pass


class AIServiceError(WellbeingError):
    """Raised when AI service operations fail."""

    pass


class InstanceError(WellbeingError):
    """Raised when multi-instance operations fail."""

    pass


class DataCorruptionError(WellbeingError):
    """Raised when data files are corrupted or invalid."""

    pass
