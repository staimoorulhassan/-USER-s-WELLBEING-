"""Integration tests for focus score flow.

Tests that:
- Activity can be tracked
- Focus score is calculated
- Dashboard is updated
- AI errors are handled gracefully
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime
import time

from services.ai_service import AIService
from services.tracker import TrackerService
from models.profile import UserProfile
from models.activity_log import ActivityLogEntry


class TestFocusScoreFlow:
    """Integration tests for complete focus score workflow."""

    @pytest.fixture
    def temp_log_path(self, tmp_path):
        """Provide temporary log file path."""
        return tmp_path / "logs.json"

    @pytest.fixture
    def mock_profile(self):
        """Provide mock user profile."""
        return UserProfile(
            name="Jane",
            role="Designer",
            main_goal="Create intuitive user interfaces",
        )

    def test_track_and_calculate_score(self, temp_log_path, mock_profile):
        """Test tracking activity and calculating focus score."""
        with patch("services.tracker.LOGS_FILE", temp_log_path), patch(
            "services.ai_service.genai"
        ) as mock_genai:
            # Mock Gemini API
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = "Focus Score: 75"
            mock_model.generate_content.return_value = mock_response

            # Create AI service
            ai_service = AIService()

            # Simulate some activity logs
            logs = [
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="Figma",
                    raw_window_title="Figma",
                    application="Figma",
                    duration_seconds=300,
                ),
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="Adobe XD",
                    raw_window_title="Adobe XD",
                    application="Adobe XD",
                    duration_seconds=200,
                ),
            ]

            # Calculate focus score
            score = ai_service.calculate_focus_score(logs, mock_profile)

            # Verify score was calculated
            assert score == 75

    def test_update_dashboard_with_score(self, temp_log_path, mock_profile):
        """Test that dashboard updates when focus score is calculated."""
        with patch("services.tracker.LOGS_FILE", temp_log_path), patch(
            "services.ai_service.genai"
        ) as mock_genai:
            # Mock Gemini API
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = "Focus Score: 82"
            mock_model.generate_content.return_value = mock_response

            # Create AI service
            ai_service = AIService()

            # Calculate score
            logs = [
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="VSCode",
                    raw_window_title="Visual Studio Code",
                    application="VSCode",
                    duration_seconds=600,
                )
            ]

            score = ai_service.calculate_focus_score(logs, mock_profile)

            # Verify score is accessible
            assert score == 82

            # Get latest score
            latest_score = ai_service.get_latest_focus_score()
            assert latest_score == score

    def test_handle_ai_api_errors(self, temp_log_path, mock_profile):
        """Test that AI API errors are handled gracefully."""
        with patch("services.tracker.LOGS_FILE", temp_log_path), patch(
            "services.ai_service.genai"
        ) as mock_genai:
            # Mock API error
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_model.generate_content.side_effect = Exception("API Error")

            # Create AI service
            ai_service = AIService()

            # Try to calculate score
            logs = [
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="Test",
                    raw_window_title="Test",
                    application="Test",
                    duration_seconds=100,
                )
            ]

            score = ai_service.calculate_focus_score(logs, mock_profile)

            # Should handle error gracefully
            assert score is None

    def test_focus_score_with_mixed_productivity(self, temp_log_path, mock_profile):
        """Test focus score calculation with productive and distracting activities."""
        with patch("services.tracker.LOGS_FILE", temp_log_path), patch(
            "services.ai_service.genai"
        ) as mock_genai:
            # Mock Gemini API
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = "Your focus score is 65."
            mock_model.generate_content.return_value = mock_response

            # Create AI service
            ai_service = AIService()

            # Mix of productive and distracting activities
            logs = [
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="Visual Studio Code",
                    raw_window_title="Visual Studio Code",
                    application="VSCode",
                    duration_seconds=300,
                ),
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="YouTube",
                    raw_window_title="YouTube - Google Chrome",
                    application="Chrome",
                    duration_seconds=200,
                ),
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="GitHub",
                    raw_window_title="GitHub - Google Chrome",
                    application="Chrome",
                    duration_seconds=150,
                ),
            ]

            score = ai_service.calculate_focus_score(logs, mock_profile)

            # Should calculate a score
            assert score == 65

    def test_focus_score_persists_across_calculations(self, temp_log_path, mock_profile):
        """Test that previous score is available if new calculation fails."""
        with patch("services.tracker.LOGS_FILE", temp_log_path), patch(
            "services.ai_service.genai"
        ) as mock_genai:
            # Mock Gemini API
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model

            # First call succeeds
            mock_response_1 = MagicMock()
            mock_response_1.text = "Focus Score: 80"
            mock_model.generate_content.return_value = mock_response_1

            # Create AI service
            ai_service = AIService()

            logs = [
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="Test",
                    raw_window_title="Test",
                    application="Test",
                    duration_seconds=100,
                )
            ]

            # First calculation
            score1 = ai_service.calculate_focus_score(logs, mock_profile)
            assert score1 == 80

            # Second call fails
            mock_model.generate_content.side_effect = Exception("API Error")
            score2 = ai_service.calculate_focus_score(logs, mock_profile)

            # Should return None on failure
            assert score2 is None

            # But previous score should still be accessible
            latest = ai_service.get_latest_focus_score()
            assert latest == 80

    def test_empty_activity_logs_handled(self, temp_log_path, mock_profile):
        """Test that empty activity logs are handled properly."""
        with patch("services.tracker.LOGS_FILE", temp_log_path), patch(
            "services.ai_service.genai"
        ) as mock_genai:
            # Mock Gemini API
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model

            # Create AI service
            ai_service = AIService()

            # Empty logs
            score = ai_service.calculate_focus_score([], mock_profile)

            # Should return None or handle gracefully
            assert score is None

            # API should not be called for empty logs
            mock_model.generate_content.assert_not_called()
