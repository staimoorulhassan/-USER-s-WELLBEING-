"""Profile service for managing user profile data.

Handles loading, saving, and validating user profiles.
"""

import logging
from typing import Optional

from config.constants import PROFILE_FILE
from models.profile import UserProfile
from utils.file_handler import read_json, write_json
from utils.exceptions import DataCorruptionError

logger = logging.getLogger(__name__)


class ProfileService:
    """Service for managing user profile operations."""

    def __init__(self, profile_path=None):
        """Initialize profile service.

        Args:
            profile_path: Custom profile file path (defaults to PROFILE_FILE)
        """
        self.profile_path = profile_path or PROFILE_FILE

    def load_profile(self) -> Optional[UserProfile]:
        """Load user profile from file.

        Returns:
            UserProfile instance if file exists and is valid
            None if file doesn't exist

        Raises:
            DataCorruptionError: If profile file is corrupted
        """
        data = read_json(self.profile_path)

        if data is None:
            logger.info(f"No profile file found at {self.profile_path}")
            return None

        try:
            profile = UserProfile.from_dict(data)
            logger.info(f"Successfully loaded profile for {profile.name}")
            return profile
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse profile: {e}")
            raise DataCorruptionError(f"Invalid profile data: {e}") from e

    def save_profile(self, name: str, role: str, main_goal: str) -> UserProfile:
        """Create or update user profile.

        Args:
            name: User's name
            role: User's role
            main_goal: User's main goal

        Returns:
            Created or updated UserProfile

        Raises:
            ValidationError: If input validation fails
            FileHandlerError: If file write fails
        """
        # Check if updating existing profile
        existing_profile = self.load_profile()

        if existing_profile:
            # Update existing profile
            existing_profile.update(name=name, role=role, main_goal=main_goal)
            profile = existing_profile
            logger.info(f"Updating existing profile for {name}")
        else:
            # Create new profile
            profile = UserProfile(name=name, role=role, main_goal=main_goal)
            logger.info(f"Creating new profile for {name}")

        # Save to file
        write_json(self.profile_path, profile.to_dict())
        logger.info(f"Profile saved to {self.profile_path}")

        return profile

    def profile_exists(self) -> bool:
        """Check if profile file exists.

        Returns:
            True if profile file exists
        """
        return self.profile_path.exists()
