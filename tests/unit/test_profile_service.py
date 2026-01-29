"""Unit tests for profile service update functionality.

Tests that:
- Profile fields can be updated
- Validation works on updates
- File is overwritten with new data
- Timestamp is updated
"""

import pytest
from pathlib import Path
from unittest.mock import patch
from datetime import datetime
import json

from services.profile_service import ProfileService
from models.profile import UserProfile


class TestProfileServiceUpdate:
    """Test profile update functionality."""

    @pytest.fixture
    def temp_profile_path(self, tmp_path):
        """Provide temporary profile file path."""
        return tmp_path / "profile.json"

    @pytest.fixture
    def existing_profile(self, temp_profile_path):
        """Create an existing profile for testing updates."""
        profile_data = {
            "name": "John",
            "role": "Developer",
            "main_goal": "Build software",
            "created_at": "2025-01-27T10:00:00",
            "last_updated": "2025-01-27T10:00:00",
        }
        temp_profile_path.write_text(json.dumps(profile_data))
        return profile_data

    def test_update_role(self, temp_profile_path, existing_profile):
        """Test updating role field."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # Update role
            updated = service.save_profile(
                name="John",
                role="Senior Developer",
                main_goal="Build software"
            )

            # Verify role changed
            assert updated.role == "Senior Developer"

            # Verify other fields unchanged
            assert updated.name == "John"
            assert updated.main_goal == "Build software"

            # Verify timestamp updated
            assert updated.last_updated > updated.created_at

    def test_update_goal(self, temp_profile_path, existing_profile):
        """Test updating main goal."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # Update goal
            updated = service.save_profile(
                name="John",
                role="Developer",
                main_goal="Build high-quality, scalable software solutions"
            )

            # Verify goal changed
            assert updated.main_goal == "Build high-quality, scalable software solutions"

            # Verify created_at unchanged
            assert updated.created_at.day == 27

    def test_update_multiple_fields(self, temp_profile_path, existing_profile):
        """Test updating multiple fields simultaneously."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # Update all fields
            updated = service.save_profile(
                name="Jane",
                role="Tech Lead",
                main_goal="Lead team to build great products"
            )

            # Verify all fields updated
            assert updated.name == "Jane"
            assert updated.role == "Tech Lead"
            assert updated.main_goal == "Lead team to build great products"

            # Verify timestamp updated
            assert updated.last_updated > updated.created_at

    def test_update_validation_fails_on_empty_name(self, temp_profile_path, existing_profile):
        """Test that update fails validation with empty name."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # Try to update with empty name
            with pytest.raises(Exception):  # ValidationError
                service.save_profile(
                    name="",
                    role="Developer",
                    main_goal="Build software"
                )

            # Verify original file unchanged
            data = json.loads(temp_profile_path.read_text())
            assert data["name"] == "John"

    def test_update_validation_fails_on_name_too_long(self, temp_profile_path, existing_profile):
        """Test that update fails validation with name exceeding max length."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # Try to update with too-long name
            long_name = "A" * 101
            with pytest.raises(Exception):
                service.save_profile(
                    name=long_name,
                    role="Developer",
                    main_goal="Build software"
                )

            # Verify original file unchanged
            data = json.loads(temp_profile_path.read_text())
            assert data["name"] == "John"

    def test_file_overwritten_on_update(self, temp_profile_path, existing_profile):
        """Test that profile file is overwritten with new data."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # Update profile
            service.save_profile(
                name="Jonathan",
                role="Senior Developer",
                main_goal="Build software"
            )

            # Verify file updated
            data = json.loads(temp_profile_path.read_text())
            assert data["name"] == "Jonathan"
            assert data["role"] == "Senior Developer"
            assert data["main_goal"] == "Build software"

    def test_timestamp_increments_on_multiple_updates(self, temp_profile_path, existing_profile):
        """Test that last_updated timestamp changes with each update."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # First update
            profile1 = service.save_profile(
                name="John",
                role="Developer",
                main_goal="Build software"
            )
            timestamp1 = profile1.last_updated

            # Small delay
            import time
            time.sleep(0.01)

            # Second update
            profile2 = service.save_profile(
                name="John",
                role="Senior Developer",
                main_goal="Build software"
            )
            timestamp2 = profile2.last_updated

            # Verify timestamp increased
            assert timestamp2 > timestamp1

    def test_created_at_preserved_on_update(self, temp_profile_path, existing_profile):
        """Test that created_at timestamp is preserved during updates."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # Load profile
            original = service.load_profile()
            original_created = original.created_at

            # Update profile
            updated = service.save_profile(
                name="John",
                role="Senior Developer",
                main_goal="Build software"
            )

            # Verify created_at unchanged
            assert updated.created_at == original_created

    def test_profile_model_update_method(self):
        """Test UserProfile model update method."""
        profile = UserProfile(
            name="Test User",
            role="Developer",
            main_goal="Test goal"
        )

        original_timestamp = profile.last_updated

        # Update using model method
        import time
        time.sleep(0.01)
        profile.update(role="Senior Developer")

        # Verify field updated
        assert profile.role == "Senior Developer"

        # Verify timestamp updated
        assert profile.last_updated > original_timestamp

        # Verify other fields unchanged
        assert profile.name == "Test User"
        assert profile.main_goal == "Test goal"
