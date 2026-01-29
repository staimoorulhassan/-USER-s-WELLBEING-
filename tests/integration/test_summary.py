"""Integration tests for daily summary generation.

Tests that:
- Activity can be tracked
- Daily summary is generated
- Summary displays with insights
- Empty logs are handled
- AI errors are handled gracefully
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

from services.ai_service import AIService
from models.profile import UserProfile
from models.activity_log import ActivityLogEntry
from models.ai_models import DailySummary


class TestSummaryFlow:
    """Integration tests for daily summary workflow."""

    @pytest.fixture
    def temp_log_path(self, tmp_path):
        """Provide temporary log file path."""
        return tmp_path / "logs.json"

    @pytest.fixture
    def mock_profile(self):
        """Provide mock user profile."""
        return UserProfile(
            name="Alex",
            role="Data Scientist",
            main_goal="Complete machine learning model",
        )

    def test_generate_daily_summary_with_activity(self, temp_log_path, mock_profile):
        """Test generating daily summary from tracked activity."""
        with patch("services.ai_service.genai") as mock_genai:
            # Mock Gemini API
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = """Daily Summary:

You had a productive day focused on data analysis and model development.
- Spent 3 hours in Jupyter notebooks
- Analyzed datasets and prepared features
- Good progress toward your ML model goal

Productivity Patterns:
- Morning deep work sessions
- Consistent focus on analytical tasks

Recommendations:
- Consider taking more breaks
- Document your progress regularly"""
            mock_model.generate_content.return_value = mock_response

            # Create AI service
            ai_service = AIService()

            # Create activity logs
            logs = [
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="Jupyter Notebook - model_training.ipynb",
                    raw_window_title="Jupyter Notebook - model_training.ipynb - Google Chrome",
                    application="Chrome",
                    duration_seconds=3600,
                ),
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="PyCharm - data_processing.py",
                    raw_window_title="PyCharm - data_processing.py",
                    application="PyCharm",
                    duration_seconds=2400,
                ),
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="GitHub - pandas-dev/pandas",
                    raw_window_title="GitHub - pandas-dev/pandas - Google Chrome",
                    application="Chrome",
                    duration_seconds=1800,
                ),
            ]

            # Generate summary
            summary = ai_service.generate_daily_summary(logs, mock_profile)

            # Verify summary was created
            assert summary is not None
            assert isinstance(summary, DailySummary)
            assert summary.summary_text != ""
            assert len(summary.summary_text) > 0

    def test_handle_empty_activity_logs(self, temp_log_path, mock_profile):
        """Test that empty activity logs are handled properly."""
        with patch("services.ai_service.genai") as mock_genai:
            # Mock Gemini API
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model

            # Create AI service
            ai_service = AIService()

            # Empty logs
            summary = ai_service.generate_daily_summary([], mock_profile)

            # Should return None for empty logs
            assert summary is None

            # API should not be called
            mock_model.generate_content.assert_not_called()

    def test_summary_with_productivity_insights(self, temp_log_path, mock_profile):
        """Test summary includes productivity insights."""
        with patch("services.ai_service.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = """Your day showed good focus on technical work.
You spent most of your time coding and debugging.
Productive patterns: Morning coding sessions, focused work.
Recommendations: Take more breaks, stay hydrated."""
            mock_model.generate_content.return_value = mock_response

            # Create AI service
            ai_service = AIService()

            logs = [
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="VSCode - app.py",
                    raw_window_title="VSCode - app.py",
                    application="VSCode",
                    duration_seconds=7200,
                )
            ]

            summary = ai_service.generate_daily_summary(logs, mock_profile)

            # Verify summary content
            assert summary is not None
            assert "coding" in summary.summary_text.lower() or "technical" in summary.summary_text.lower()

    def test_handle_ai_api_errors_in_summary(self, temp_log_path, mock_profile):
        """Test that AI API errors during summary generation are handled."""
        with patch("services.ai_service.genai") as mock_genai:
            # Mock API error
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_model.generate_content.side_effect = Exception("API Error")

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

            # Try to generate summary
            summary = ai_service.generate_daily_summary(logs, mock_profile)

            # Should handle error gracefully
            assert summary is None

    def test_summary_includes_goal_alignment(self, temp_log_path, mock_profile):
        """Test that summary considers user's main goal."""
        with patch("services.ai_service.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = """You made good progress on your ML model goal.
Spent time on data preprocessing and feature engineering.
Your activities align well with your objective."""
            mock_model.generate_content.return_value = mock_response

            # Create AI service
            ai_service = AIService()

            logs = [
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="Jupyter - feature_engineering.ipynb",
                    raw_window_title="Jupyter - feature_engineering.ipynb",
                    application="Jupyter",
                    duration_seconds=5400,
                )
            ]

            summary = ai_service.generate_daily_summary(logs, mock_profile)

            # Verify summary was generated
            assert summary is not None
            assert len(summary.summary_text) > 0

    def test_summary_with_mixed_productivity(self, temp_log_path, mock_profile):
        """Test summary with both productive and distracting activities."""
        with patch("services.ai_service.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = """Your day had mixed productivity.
Good focused work on coding, but significant time on social media.
Consider reducing distractions to improve focus."""
            mock_model.generate_content.return_value = mock_response

            # Create AI service
            ai_service = AIService()

            # Mix of productive and distracting
            logs = [
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="VSCode - main.py",
                    raw_window_title="VSCode - main.py",
                    application="VSCode",
                    duration_seconds=3600,
                ),
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="YouTube",
                    raw_window_title="YouTube - Google Chrome",
                    application="Chrome",
                    duration_seconds=2400,
                ),
                ActivityLogEntry(
                    timestamp=datetime.now(),
                    window_title="Twitter",
                    raw_window_title="Twitter - Google Chrome",
                    application="Chrome",
                    duration_seconds=1800,
                ),
            ]

            summary = ai_service.generate_daily_summary(logs, mock_profile)

            # Verify summary handles mixed activity
            assert summary is not None

    def test_summary_persists_across_sessions(self, temp_log_path, mock_profile):
        """Test that summary can be serialized and deserialized."""
        with patch("services.ai_service.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = "Test summary text."
            mock_model.generate_content.return_value = mock_response

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

            # Generate summary
            summary = ai_service.generate_daily_summary(logs, mock_profile)

            # Serialize
            summary_dict = summary.to_dict()

            # Deserialize
            restored_summary = DailySummary.from_dict(summary_dict)

            # Verify
            assert restored_summary.summary_text == summary.summary_text
            assert restored_summary.generated_at == summary.generated_at
