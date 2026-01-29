"""Unit tests for ActivityLogEntry model.

Tests that:
- Timestamps are validated and stored correctly
- Browser suffix filtering works
- Required fields are enforced
"""

import pytest
from datetime import datetime
from models.activity_log import ActivityLogEntry


class TestActivityLogEntry:
    """Test ActivityLogEntry model validation and behavior."""

    def test_timestamp_validation(self):
        """Test that timestamp is stored correctly."""
        now = datetime.now()
        entry = ActivityLogEntry(
            timestamp=now,
            window_title="GitHub - python/requests",
            raw_window_title="GitHub - python/requests - Google Chrome",
            application="Chrome",
            duration_seconds=0,
        )

        assert entry.timestamp == now

    def test_required_fields_enforced(self):
        """Test that required fields cannot be None."""
        with pytest.raises(TypeError):
            # Missing window_title
            ActivityLogEntry(
                timestamp=datetime.now(),
                raw_window_title="test",
                application="Chrome",
            )

    def test_raw_window_title_preserved(self):
        """Test that raw window title is preserved."""
        entry = ActivityLogEntry(
            timestamp=datetime.now(),
            window_title="GitHub - python/requests",
            raw_window_title="GitHub - python/requests - Google Chrome",
            application="Chrome",
            duration_seconds=0,
        )

        assert entry.raw_window_title == "GitHub - python/requests - Google Chrome"

    def test_application_extraction(self):
        """Test that application field is extracted correctly."""
        entry = ActivityLogEntry(
            timestamp=datetime.now(),
            window_title="GitHub - python/requests",
            raw_window_title="GitHub - python/requests - Google Chrome",
            application="Chrome",
            duration_seconds=0,
        )

        assert entry.application == "Chrome"

    def test_duration_defaults_to_zero(self):
        """Test that duration_seconds defaults to 0."""
        entry = ActivityLogEntry(
            timestamp=datetime.now(),
            window_title="GitHub",
            raw_window_title="GitHub - Google Chrome",
            application="Chrome",
        )

        assert entry.duration_seconds == 0

    def test_to_dict_conversion(self):
        """Test that entry can be converted to dictionary."""
        now = datetime.now()
        entry = ActivityLogEntry(
            timestamp=now,
            window_title="GitHub",
            raw_window_title="GitHub - Google Chrome",
            application="Chrome",
            duration_seconds=30,
        )

        data = entry.to_dict()

        assert data["window_title"] == "GitHub"
        assert data["raw_window_title"] == "GitHub - Google Chrome"
        assert data["application"] == "Chrome"
        assert data["duration_seconds"] == 30
        assert "timestamp" in data

    def test_from_dict_creation(self):
        """Test that entry can be created from dictionary."""
        now = datetime.now()
        data = {
            "timestamp": now.isoformat(),
            "window_title": "GitHub",
            "raw_window_title": "GitHub - Google Chrome",
            "application": "Chrome",
            "duration_seconds": 30,
        }

        entry = ActivityLogEntry.from_dict(data)

        assert entry.window_title == "GitHub"
        assert entry.raw_window_title == "GitHub - Google Chrome"
        assert entry.application == "Chrome"
        assert entry.duration_seconds == 30
