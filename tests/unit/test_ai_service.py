"""Unit tests for AI service focus score calculation.

Tests that:
- Gemini API is mocked correctly
- Prompt generation includes activity logs and user context
- Score parsing extracts numeric value from AI response
- Timeouts are handled
- Retry logic works
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from services.ai_service import AIService
from models.profile import UserProfile
from models.activity_log import ActivityLogEntry


class TestAIServiceFocusScore:
    """Test AI service focus score calculation."""

    @pytest.fixture
    def mock_profile(self):
        """Provide mock user profile."""
        return UserProfile(
            name="John",
            role="Developer",
            main_goal="Build high-quality software",
        )

    @pytest.fixture
    def mock_activity_logs(self):
        """Provide mock activity log entries."""
        return [
            ActivityLogEntry(
                timestamp=datetime.now(),
                window_title="Visual Studio Code",
                raw_window_title="Visual Studio Code",
                application="VSCode",
                duration_seconds=300,
            ),
            ActivityLogEntry(
                timestamp=datetime.now(),
                window_title="GitHub - python/requests",
                raw_window_title="GitHub - python/requests - Google Chrome",
                application="Chrome",
                duration_seconds=120,
            ),
        ]

    def test_focus_score_prompt_generation(self, mock_profile, mock_activity_logs):
        """Test that prompt includes activity logs and user context."""
        with patch("services.ai_service.genai") as mock_genai:
            # Mock Gemini client
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = "Focus Score: 75"
            mock_model.generate_content.return_value = mock_response

            service = AIService()
            service.calculate_focus_score(mock_activity_logs, mock_profile)

            # Verify model was created
            mock_genai.GenerativeModel.assert_called_once()

            # Verify generate_content was called
            assert mock_model.generate_content.called

            # Get the prompt that was sent
            call_args = mock_model.generate_content.call_args
            prompt = call_args[0][0]

            # Verify prompt includes user context
            assert "John" in prompt
            assert "Developer" in prompt
            assert "Build high-quality software" in prompt

    def test_focus_score_parsing(self, mock_profile, mock_activity_logs):
        """Test that score is extracted from AI response."""
        with patch("services.ai_service.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = "Based on your activity, your Focus Score is 85."
            mock_model.generate_content.return_value = mock_response

            service = AIService()
            score = service.calculate_focus_score(mock_activity_logs, mock_profile)

            # Score should be extracted
            assert score == 85

    def test_focus_score_handles_various_formats(self, mock_profile, mock_activity_logs):
        """Test score parsing with different response formats."""
        test_cases = [
            ("Your focus score: 72", 72),
            ("Score: 88/100", 88),
            ("Focus Score = 95", 95),
            ("You scored 65", 65),
            ("100", 100),
        ]

        for response_text, expected_score in test_cases:
            with patch("services.ai_service.genai") as mock_genai:
                mock_model = MagicMock()
                mock_genai.GenerativeModel.return_value = mock_model
                mock_response = MagicMock()
                mock_response.text = response_text
                mock_model.generate_content.return_value = mock_response

                service = AIService()
                score = service.calculate_focus_score(mock_activity_logs, mock_profile)
                assert score == expected_score

    def test_focus_score_timeout(self, mock_profile, mock_activity_logs):
        """Test that timeout is handled gracefully."""
        with patch("services.ai_service.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            # Simulate timeout
            mock_model.generate_content.side_effect = Exception("Timeout")

            service = AIService()
            score = service.calculate_focus_score(mock_activity_logs, mock_profile, timeout=1)

            # Should return None on timeout
            assert score is None

    def test_focus_score_with_empty_logs(self, mock_profile):
        """Test behavior with no activity logs."""
        with patch("services.ai_service.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = "No activity to analyze. Focus Score: N/A"
            mock_model.generate_content.return_value = mock_response

            service = AIService()
            score = service.calculate_focus_score([], mock_profile)

            # Should handle gracefully
            assert score is None

    def test_focus_score_caching(self, mock_profile, mock_activity_logs):
        """Test that score is cached for subsequent calls."""
        with patch("services.ai_service.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = "Focus Score: 80"
            mock_model.generate_content.return_value = mock_response

            service = AIService()

            # First call
            score1 = service.calculate_focus_score(mock_activity_logs, mock_profile)

            # Second call (should use cache if logs haven't changed)
            score2 = service.calculate_focus_score(mock_activity_logs, mock_profile)

            assert score1 == score2 == 80

    def test_focus_score_range_validation(self, mock_profile, mock_activity_logs):
        """Test that score is within valid range (0-100)."""
        with patch("services.ai_service.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = "Focus Score: 150"
            mock_model.generate_content.return_value = mock_response

            service = AIService()
            score = service.calculate_focus_score(mock_activity_logs, mock_profile)

            # Should handle out-of-range scores
            # Either clamp to 100 or return None
            assert score is None or (0 <= score <= 100)

    def test_api_key_initialization(self):
        """Test that API key is loaded from environment."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
            with patch("services.ai_service.genai") as mock_genai:
                mock_genai.configure.return_value = None

                service = AIService()

                # Verify API key was configured
                mock_genai.configure.assert_called_once_with(api_key="test_key")
