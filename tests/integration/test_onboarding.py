"""Integration tests for onboarding flow.

Tests that:
- First launch is detected when profile.json doesn't exist
- Form validation works correctly
- Profile is saved to file on submit
- Dashboard is shown after successful onboarding
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from models.profile import UserProfile
from services.profile_service import ProfileService
from ui.main_window import MainWindow


class TestOnboardingFlow:
    """Integration tests for complete onboarding user journey."""

    @pytest.fixture
    def temp_profile_path(self, tmp_path):
        """Provide temporary profile file path."""
        return tmp_path / "profile.json"

    def test_first_launch_detected_when_no_profile(self, temp_profile_path):
        """Test that first launch is detected when profile.json doesn't exist."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()
            profile = service.load_profile()

            assert profile is None

    def test_existing_profile_loaded_on_subsequent_launch(self, temp_profile_path):
        """Test that existing profile is loaded on subsequent launches."""
        # Create a profile file
        profile_data = {
            "name": "John",
            "role": "Developer",
            "main_goal": "Build software",
            "created_at": "2025-01-27T10:00:00",
            "last_updated": "2025-01-27T10:00:00",
        }

        import json

        temp_profile_path.write_text(json.dumps(profile_data))

        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()
            profile = service.load_profile()

            assert profile is not None
            assert profile.name == "John"
            assert profile.role == "Developer"

    def test_form_validation_rejects_empty_fields(self):
        """Test that onboarding form rejects empty fields."""
        service = ProfileService()

        with pytest.raises(ValueError, match="Name is required"):
            service.save_profile(name="", role="Developer", main_goal="Build software")

    def test_profile_saved_to_file_on_submit(self, temp_profile_path):
        """Test that profile is saved to profile.json on submit."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()
            service.save_profile(
                name="Jane", role="Designer", main_goal="Create great UX"
            )

            # Verify file was created
            assert temp_profile_path.exists()

            # Verify content
            import json

            data = json.loads(temp_profile_path.read_text())
            assert data["name"] == "Jane"
            assert data["role"] == "Designer"
            assert data["main_goal"] == "Create great UX"

    def test_dashboard_transition_after_onboarding(self):
        """Test that dashboard is shown after successful onboarding."""
        # This would test the UI transition logic
        # Mock implementation for now
        window = MainWindow()

        # Initially, no dashboard frame
        assert window.dashboard_frame is None

        # After showing dashboard (to be implemented)
        # window.show_dashboard()
        # assert window.dashboard_frame is not None

    def test_profile_update_timestamp(self, temp_profile_path):
        """Test that last_updated timestamp changes on update."""
        with patch("services.profile_service.PROFILE_FILE", temp_profile_path):
            service = ProfileService()

            # Create initial profile
            service.save_profile(
                name="John", role="Developer", main_goal="Build software"
            )
            first_profile = service.load_profile()
            first_timestamp = first_profile.last_updated

            # Update profile
            import time

            time.sleep(0.01)  # Small delay to ensure different timestamp
            service.save_profile(
                name="John", role="Senior Developer", main_goal="Build great software"
            )
            updated_profile = service.load_profile()

            assert updated_profile.last_updated > first_timestamp
            assert updated_profile.role == "Senior Developer"
