"""Integration tests for settings/profile management flow.

Tests that:
- Settings can be opened
- Profile can be edited
- Changes are saved
- Profile.json is updated
- Validation works in settings
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

from services.profile_service import ProfileService
from models.profile import UserProfile


class TestSettingsFlow:
    """Integration tests for settings workflow."""

    @pytest.fixture
    def temp_profile_path(self, tmp_path):
        """Provide temporary profile file path."""
        return tmp_path / "profile.json"

    @pytest.fixture
    def existing_profile(self, temp_profile_path):
        """Create an existing profile."""
        profile_data = {
            "name": "Alice",
            "role": "Designer",
            "main_goal": "Create beautiful designs",
            "created_at": "2025-01-27T10:00:00",
            "last_updated": "2025-01-27T10:00:00",
        }
        temp_profile_path.write_text(json.dumps(profile_data))
        return profile_data

    def test_open_settings_loads_profile(self, temp_profile_path, existing_profile):
        """Test that opening settings loads existing profile."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()
            profile = service.load_profile()

            # Verify profile loaded
            assert profile is not None
            assert profile.name == "Alice"
            assert profile.role == "Designer"
            assert profile.main_goal == "Create beautiful designs"

    def test_edit_profile_in_settings(self, temp_profile_path, existing_profile):
        """Test editing profile fields in settings."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # Simulate user editing fields
            new_name = "Alice Smith"
            new_role = "Senior Designer"
            new_goal = "Create beautiful, user-centered designs"

            # Save changes
            updated = service.save_profile(
                name=new_name,
                role=new_role,
                main_goal=new_goal
            )

            # Verify changes saved
            assert updated.name == new_name
            assert updated.role == new_role
            assert updated.main_goal == new_goal

    def test_save_updates_profile_file(self, temp_profile_path, existing_profile):
        """Test that saving updates profile.json file."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # Update profile
            service.save_profile(
                name="Alice",
                role="UX Designer",
                main_goal="Create intuitive user experiences"
            )

            # Verify file updated
            data = json.loads(temp_profile_path.read_text())
            assert data["role"] == "UX Designer"
            assert data["main_goal"] == "Create intuitive user experiences"

    def test_cancel_does_not_save_changes(self, temp_profile_path, existing_profile):
        """Test that canceling doesn't save changes (simulated)."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # Load original
            original = service.load_profile()
            original_role = original.role

            # Simulate user making changes but canceling
            # (don't call save_profile)

            # Verify file unchanged
            data = json.loads(temp_profile_path.read_text())
            assert data["role"] == original_role

    def test_validation_in_settings(self, temp_profile_path, existing_profile):
        """Test that validation works in settings context."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # Try to save invalid profile
            with pytest.raises(Exception):
                service.save_profile(
                    name="",  # Empty name
                    role="Designer",
                    main_goal="Create designs"
                )

            # Verify original profile unchanged
            data = json.loads(temp_profile_path.read_text())
            assert data["name"] == "Alice"

    def test_reflected_in_summaries(self, temp_profile_path, existing_profile):
        """Test that profile changes are reflected when used in summaries."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # Update profile
            updated = service.save_profile(
                name="Alice",
                role="Product Designer",
                main_goal="Design products users love"
            )

            # Verify new values available
            assert updated.role == "Product Designer"

            # These would be used in AI summaries
            # Simulate usage
            role_context = f"User is a {updated.role}"
            goal_context = f"Main goal: {updated.main_goal}"

            assert "Product Designer" in role_context
            assert "Design products users love" in goal_context

    def test_multiple_updates_in_session(self, temp_profile_path, existing_profile):
        """Test multiple profile updates in one session."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # First update
            service.save_profile(
                name="Alice",
                role="UX Designer",
                main_goal="Create great UX"
            )

            # Second update
            service.save_profile(
                name="Alice",
                role="Senior UX Designer",
                main_goal="Create great UX and mentor others"
            )

            # Verify final state
            profile = service.load_profile()
            assert profile.role == "Senior UX Designer"
            assert profile.main_goal == "Create great UX and mentor others"

    def test_profile_persistence_across_reloads(self, temp_profile_path, existing_profile):
        """Test that profile persists across service reloads."""
        # First service instance
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service1 = ProfileService()
            service1.save_profile(
                name="Alice",
                role="Lead Designer",
                main_goal="Lead design team"
            )

        # New service instance (simulating app restart)
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service2 = ProfileService()
            profile = service2.load_profile()

            # Verify changes persisted
            assert profile.role == "Lead Designer"
            assert profile.main_goal == "Lead design team"

    def test_name_cannot_be_empty(self, temp_profile_path, existing_profile):
        """Test that name cannot be updated to empty string."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            with pytest.raises(Exception):
                service.save_profile(
                    name="   ",  # Whitespace only
                    role="Designer",
                    main_goal="Create designs"
                )

            # Verify unchanged
            profile = service.load_profile()
            assert profile.name == "Alice"

    def test_trim_whitespace_on_update(self, temp_profile_path, existing_profile):
        """Test that whitespace is trimmed from fields on update."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # Update with extra whitespace
            updated = service.save_profile(
                name="  Alice  ",
                role="  Senior Designer  ",
                main_goal="  Create designs  "
            )

            # Verify whitespace trimmed
            assert updated.name == "Alice"
            assert updated.role == "Senior Designer"
            assert updated.main_goal == "Create designs"
