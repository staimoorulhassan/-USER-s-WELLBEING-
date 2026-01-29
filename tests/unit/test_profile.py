"""Unit tests for UserProfile model validation.

Tests that:
- Empty fields are rejected
- Max length constraints are enforced
- Timestamps are auto-generated
- Validation methods work correctly
"""

import pytest
from datetime import datetime
from models.profile import UserProfile


class TestUserProfileValidation:
    """Test UserProfile validation rules."""

    def test_empty_name_rejected(self):
        """Test that empty name raises ValidationError."""
        with pytest.raises(ValueError, match="Name is required"):
            UserProfile(name="", role="Developer", main_goal="Build software")

    def test_empty_role_rejected(self):
        """Test that empty role raises ValidationError."""
        with pytest.raises(ValueError, match="Role is required"):
            UserProfile(name="John", role="", main_goal="Build software")

    def test_empty_goal_rejected(self):
        """Test that empty main_goal raises ValidationError."""
        with pytest.raises(ValueError, match="Main goal is required"):
            UserProfile(name="John", role="Developer", main_goal="")

    def test_name_max_length_enforced(self):
        """Test that name exceeding 100 characters is rejected."""
        long_name = "A" * 101
        with pytest.raises(ValueError, match="Name must be 100 characters or less"):
            UserProfile(name=long_name, role="Developer", main_goal="Build software")

    def test_role_max_length_enforced(self):
        """Test that role exceeding 50 characters is rejected."""
        long_role = "A" * 51
        with pytest.raises(ValueError, match="Role must be 50 characters or less"):
            UserProfile(name="John", role=long_role, main_goal="Build software")

    def test_goal_max_length_enforced(self):
        """Test that goal exceeding 500 characters is rejected."""
        long_goal = "A" * 501
        with pytest.raises(ValueError, match="Main goal must be 500 characters or less"):
            UserProfile(name="John", role="Developer", main_goal=long_goal)

    def test_created_at_auto_generated(self):
        """Test that created_at timestamp is auto-generated."""
        before = datetime.now()
        profile = UserProfile(name="John", role="Developer", main_goal="Build software")
        after = datetime.now()

        assert profile.created_at is not None
        assert before <= profile.created_at <= after

    def test_last_updated_initialized_to_created_at(self):
        """Test that last_updated starts equal to created_at."""
        profile = UserProfile(name="John", role="Developer", main_goal="Build software")
        assert profile.last_updated == profile.created_at

    def test_to_dict_conversion(self):
        """Test that profile can be converted to dictionary."""
        profile = UserProfile(name="John", role="Developer", main_goal="Build software")
        data = profile.to_dict()

        assert data["name"] == "John"
        assert data["role"] == "Developer"
        assert data["main_goal"] == "Build software"
        assert "created_at" in data
        assert "last_updated" in data

    def test_from_dict_creation(self):
        """Test that profile can be created from dictionary."""
        data = {
            "name": "Jane",
            "role": "Designer",
            "main_goal": "Create great UX",
            "created_at": "2025-01-27T10:00:00",
            "last_updated": "2025-01-27T10:00:00",
        }
        profile = UserProfile.from_dict(data)

        assert profile.name == "Jane"
        assert profile.role == "Designer"
        assert profile.main_goal == "Create great UX"

    def test_whitespace_trimming(self):
        """Test that leading/trailing whitespace is trimmed from fields."""
        profile = UserProfile(
            name="  John  ", role="  Developer  ", main_goal="  Build software  "
        )
        assert profile.name == "John"
        assert profile.role == "Developer"
        assert profile.main_goal == "Build software"
