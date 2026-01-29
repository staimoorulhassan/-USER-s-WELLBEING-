"""Unit tests for WorkState model."""

import pytest
from datetime import datetime
from models.work_state import WorkState


class TestWorkStateModel:
    """Test suite for WorkState model validation and serialization."""

    def test_create_work_state_with_valid_data(self):
        """Test creating a WorkState with valid data."""
        work_state = WorkState(
            session_summary="Tracked for 45m with 12 activities",
            completed_tasks=["Task 1", "Task 2"],
            timestamp="2024-01-28T10:30:00",
            streak_count=5,
            last_productive_session="2024-01-28T09:00:00",
            focus_score=75,
            total_tracking_minutes=45,
        )

        assert work_state.session_summary == "Tracked for 45m with 12 activities"
        assert work_state.completed_tasks == ["Task 1", "Task 2"]
        assert work_state.timestamp == "2024-01-28T10:30:00"
        assert work_state.streak_count == 5
        assert work_state.last_productive_session == "2024-01-28T09:00:00"
        assert work_state.focus_score == 75
        assert work_state.total_tracking_minutes == 45

    def test_create_work_state_with_optional_fields_none(self):
        """Test creating WorkState with optional fields as None."""
        work_state = WorkState(
            session_summary="Test session",
            completed_tasks=[],
            timestamp="2024-01-28T10:30:00",
            streak_count=0,
            last_productive_session=None,
            focus_score=None,
            total_tracking_minutes=0,
        )

        assert work_state.last_productive_session is None
        assert work_state.focus_score is None
        assert work_state.streak_count == 0
        assert work_state.total_tracking_minutes == 0

    def test_create_empty_work_state(self):
        """Test creating an empty WorkState using factory method."""
        work_state = WorkState.create_empty()

        assert work_state.session_summary == ""
        assert work_state.completed_tasks == []
        assert work_state.streak_count == 0
        assert work_state.last_productive_session is None
        assert work_state.focus_score is None
        assert work_state.total_tracking_minutes == 0
        # Timestamp should be a valid ISO format string
        assert isinstance(work_state.timestamp, str)
        assert len(work_state.timestamp) > 0

    def test_validation_negative_streak_count_raises_error(self):
        """Test that negative streak_count raises ValueError."""
        with pytest.raises(ValueError, match="streak_count must be >= 0"):
            WorkState(
                session_summary="Test",
                completed_tasks=[],
                timestamp="2024-01-28T10:30:00",
                streak_count=-1,  # Invalid
            )

    def test_validation_negative_tracking_minutes_raises_error(self):
        """Test that negative total_tracking_minutes raises ValueError."""
        with pytest.raises(ValueError, match="total_tracking_minutes must be >= 0"):
            WorkState(
                session_summary="Test",
                completed_tasks=[],
                timestamp="2024-01-28T10:30:00",
                total_tracking_minutes=-10,  # Invalid
            )

    def test_validation_focus_score_below_range_raises_error(self):
        """Test that focus_score below 0 raises ValueError."""
        with pytest.raises(ValueError, match="focus_score must be between 0 and 100"):
            WorkState(
                session_summary="Test",
                completed_tasks=[],
                timestamp="2024-01-28T10:30:00",
                focus_score=-5,  # Invalid
            )

    def test_validation_focus_score_above_range_raises_error(self):
        """Test that focus_score above 100 raises ValueError."""
        with pytest.raises(ValueError, match="focus_score must be between 0 and 100"):
            WorkState(
                session_summary="Test",
                completed_tasks=[],
                timestamp="2024-01-28T10:30:00",
                focus_score=150,  # Invalid
            )

    def test_validation_focus_score_at_boundaries(self):
        """Test that focus_score at boundaries (0 and 100) are valid."""
        # Test focus_score = 0
        work_state = WorkState(
            session_summary="Test",
            completed_tasks=[],
            timestamp="2024-01-28T10:30:00",
            focus_score=0,
        )
        assert work_state.focus_score == 0

        # Test focus_score = 100
        work_state = WorkState(
            session_summary="Test",
            completed_tasks=[],
            timestamp="2024-01-28T10:30:00",
            focus_score=100,
        )
        assert work_state.focus_score == 100

    def test_to_dict_serialization(self):
        """Test serializing WorkState to dictionary."""
        work_state = WorkState(
            session_summary="Test session",
            completed_tasks=["Task A", "Task B"],
            timestamp="2024-01-28T10:30:00",
            streak_count=3,
            last_productive_session="2024-01-28T09:00:00",
            focus_score=80,
            total_tracking_minutes=60,
        )

        data = work_state.to_dict()

        assert data["session_summary"] == "Test session"
        assert data["completed_tasks"] == ["Task A", "Task B"]
        assert data["timestamp"] == "2024-01-28T10:30:00"
        assert data["streak_count"] == 3
        assert data["last_productive_session"] == "2024-01-28T09:00:00"
        assert data["focus_score"] == 80
        assert data["total_tracking_minutes"] == 60

    def test_from_dict_deserialization(self):
        """Test deserializing WorkState from dictionary."""
        data = {
            "session_summary": "Test session",
            "completed_tasks": ["Task A"],
            "timestamp": "2024-01-28T10:30:00",
            "streak_count": 2,
            "last_productive_session": "2024-01-28T08:00:00",
            "focus_score": 65,
            "total_tracking_minutes": 30,
        }

        work_state = WorkState.from_dict(data)

        assert work_state.session_summary == "Test session"
        assert work_state.completed_tasks == ["Task A"]
        assert work_state.timestamp == "2024-01-28T10:30:00"
        assert work_state.streak_count == 2
        assert work_state.last_productive_session == "2024-01-28T08:00:00"
        assert work_state.focus_score == 65
        assert work_state.total_tracking_minutes == 30

    def test_from_dict_with_missing_required_field_raises_error(self):
        """Test that missing required fields raise KeyError."""
        incomplete_data = {
            "session_summary": "Test",
            # Missing: completed_tasks, timestamp
        }

        with pytest.raises(KeyError):
            WorkState.from_dict(incomplete_data)

    def test_from_dict_with_optional_fields_missing(self):
        """Test deserializing with optional fields missing."""
        data = {
            "session_summary": "Test session",
            "completed_tasks": [],
            "timestamp": "2024-01-28T10:30:00",
            # Missing: streak_count, last_productive_session, focus_score, total_tracking_minutes
        }

        work_state = WorkState.from_dict(data)

        # Should use defaults
        assert work_state.streak_count == 0
        assert work_state.last_productive_session is None
        assert work_state.focus_score is None
        assert work_state.total_tracking_minutes == 0

    def test_roundtrip_serialization(self):
        """Test that to_dict and from_dict preserve data correctly."""
        original = WorkState(
            session_summary="Original session",
            completed_tasks=["Task 1", "Task 2", "Task 3"],
            timestamp="2024-01-28T10:30:00",
            streak_count=10,
            last_productive_session="2024-01-27T15:00:00",
            focus_score=92,
            total_tracking_minutes=120,
        )

        # Serialize and deserialize
        data = original.to_dict()
        restored = WorkState.from_dict(data)

        # Verify all fields match
        assert restored.session_summary == original.session_summary
        assert restored.completed_tasks == original.completed_tasks
        assert restored.timestamp == original.timestamp
        assert restored.streak_count == original.streak_count
        assert restored.last_productive_session == original.last_productive_session
        assert restored.focus_score == original.focus_score
        assert restored.total_tracking_minutes == original.total_tracking_minutes

    def test_empty_completed_tasks_list(self):
        """Test WorkState with empty completed_tasks list."""
        work_state = WorkState(
            session_summary="No tasks completed",
            completed_tasks=[],  # Empty list
            timestamp="2024-01-28T10:30:00",
        )

        assert work_state.completed_tasks == []
        assert len(work_state.completed_tasks) == 0

    def test_zero_streak_count(self):
        """Test WorkState with zero streak count."""
        work_state = WorkState(
            session_summary="Test",
            completed_tasks=[],
            timestamp="2024-01-28T10:30:00",
            streak_count=0,  # Valid
        )

        assert work_state.streak_count == 0

    def test_large_completed_tasks_list(self):
        """Test WorkState with many completed tasks."""
        tasks = [f"Task {i}" for i in range(100)]
        work_state = WorkState(
            session_summary="Productive session",
            completed_tasks=tasks,
            timestamp="2024-01-28T10:30:00",
        )

        assert len(work_state.completed_tasks) == 100
        assert work_state.completed_tasks[0] == "Task 0"
        assert work_state.completed_tasks[99] == "Task 99"
