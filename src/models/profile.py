"""UserProfile model for storing user information.

Represents user profile with name, role, and main goal.
Includes validation and serialization methods.
"""

from datetime import datetime
from typing import Optional


class ValidationError(Exception):
    """Raised when profile validation fails."""

    pass


class UserProfile:
    """User profile model.

    Attributes:
        name: User's name (1-100 characters)
        role: User's role or job title (1-50 characters)
        main_goal: User's main goal or objective (1-500 characters)
        created_at: Profile creation timestamp
        last_updated: Last update timestamp
    """

    MAX_NAME_LENGTH = 100
    MAX_ROLE_LENGTH = 50
    MAX_GOAL_LENGTH = 500

    def __init__(
        self,
        name: str,
        role: str,
        main_goal: str,
        created_at: Optional[datetime] = None,
        last_updated: Optional[datetime] = None,
    ):
        """Initialize user profile with validation.

        Args:
            name: User's name
            role: User's role
            main_goal: User's main goal
            created_at: Creation timestamp (auto-generated if None)
            last_updated: Last update timestamp (defaults to created_at if None)

        Raises:
            ValidationError: If any field fails validation
        """
        # Trim whitespace
        self.name = name.strip() if name else ""
        self.role = role.strip() if role else ""
        self.main_goal = main_goal.strip() if main_goal else ""

        # Validate
        self._validate()

        # Set timestamps
        self.created_at = created_at or datetime.now()
        self.last_updated = last_updated or self.created_at

    def _validate(self) -> None:
        """Validate all profile fields.

        Raises:
            ValidationError: If validation fails
        """
        if not self.name:
            raise ValidationError("Name is required")

        if len(self.name) > self.MAX_NAME_LENGTH:
            raise ValidationError(
                f"Name must be {self.MAX_NAME_LENGTH} characters or less"
            )

        if not self.role:
            raise ValidationError("Role is required")

        if len(self.role) > self.MAX_ROLE_LENGTH:
            raise ValidationError(
                f"Role must be {self.MAX_ROLE_LENGTH} characters or less"
            )

        if not self.main_goal:
            raise ValidationError("Main goal is required")

        if len(self.main_goal) > self.MAX_GOAL_LENGTH:
            raise ValidationError(
                f"Main goal must be {self.MAX_GOAL_LENGTH} characters or less"
            )

    def to_dict(self) -> dict:
        """Convert profile to dictionary for JSON serialization.

        Returns:
            Dictionary representation of profile
        """
        return {
            "name": self.name,
            "role": self.role,
            "main_goal": self.main_goal,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        """Create profile from dictionary (deserialization).

        Args:
            data: Dictionary with profile data

        Returns:
            UserProfile instance

        Raises:
            ValidationError: If data is invalid
        """
        return cls(
            name=data["name"],
            role=data["role"],
            main_goal=data["main_goal"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
        )

    def update(self, name: Optional[str] = None, role: Optional[str] = None, main_goal: Optional[str] = None) -> None:
        """Update profile fields and refresh timestamp.

        Args:
            name: New name (optional)
            role: New role (optional)
            main_goal: New main goal (optional)

        Raises:
            ValidationError: If new values are invalid
        """
        if name is not None:
            self.name = name.strip()
        if role is not None:
            self.role = role.strip()
        if main_goal is not None:
            self.main_goal = main_goal.strip()

        # Re-validate
        self._validate()

        # Update timestamp
        self.last_updated = datetime.now()
