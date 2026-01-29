"""Integration tests for work state persistence.

Tests the complete flow of saving, loading, and updating work state.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime

from models.work_state import WorkState
from services.state_manager import StateManager
from utils.file_handler import write_json, read_json


class TestStatePersistence:
    """Test suite for work state persistence integration."""

    @pytest.fixture
    def temp_state_file(self, tmp_path):
        """Create a temporary file path for work state testing."""
        return tmp_path / "test_work_state.json"

    @pytest.fixture
    def state_manager(self, temp_state_file):
        """Create a StateManager with temporary file path."""
        return StateManager(work_state_path=temp_state_file)

    def test_save_and_load_work_state_roundtrip(self, state_manager, temp_state_file):
        """Test saving and loading work state preserves all data."""
        original_state = WorkState(
            session_summary="Test session summary",
            completed_tasks=["Task 1", "Task 2", "Task 3"],
            timestamp="2024-01-28T10:30:00",
            streak_count=5,
            last_productive_session="2024-01-28T09:00:00",
            focus_score=85,
            total_tracking_minutes=120,
        )

        # Save work state
        state_manager.save_work_state(original_state)

        # Verify file was created
        assert temp_state_file.exists()

        # Load work state
        loaded_state = state_manager.load_work_state()

        # Verify all fields match
        assert loaded_state.session_summary == original_state.session_summary
        assert loaded_state.completed_tasks == original_state.completed_tasks
        assert loaded_state.timestamp == original_state.timestamp
        assert loaded_state.streak_count == original_state.streak_count
        assert loaded_state.last_productive_session == original_state.last_productive_session
        assert loaded_state.focus_score == original_state.focus_score
        assert loaded_state.total_tracking_minutes == original_state.total_tracking_minutes

    def test_load_work_state_when_file_does_not_exist(self, state_manager, temp_state_file):
        """Test loading work state when file doesn't exist returns None."""
        # Don't create any file
        assert not temp_state_file.exists()

        # Load should return None
        loaded_state = state_manager.load_work_state()
        assert loaded_state is None

    def test_load_work_state_with_corrupted_data(self, state_manager, temp_state_file):
        """Test loading corrupted work state raises ValueError."""
        from utils.file_handler import DataCorruptionError

        # Write invalid JSON
        temp_state_file.write_text("{invalid json data")

        # Should raise DataCorruptionError (which is a subclass of ValueError)
        with pytest.raises(DataCorruptionError, match="Corrupted JSON file"):
            state_manager.load_work_state()

    def test_load_work_state_with_missing_required_field(self, state_manager, temp_state_file):
        """Test loading work state with missing required field raises error."""
        # Write incomplete data
        incomplete_data = {
            "session_summary": "Test",
            # Missing: completed_tasks, timestamp
        }
        temp_state_file.write_text(json.dumps(incomplete_data))

        # Should raise KeyError or ValueError
        with pytest.raises((KeyError, ValueError)):
            state_manager.load_work_state()

    def test_save_work_state_creates_backup(self, state_manager, temp_state_file):
        """Test that saving work state creates backup files."""
        # Create initial state
        state1 = WorkState.create_empty()
        state_manager.save_work_state(state1)

        # Save a second time (should create backup)
        state2 = WorkState(
            session_summary="Updated session",
            completed_tasks=["New Task"],
            timestamp="2024-01-28T11:00:00",
            streak_count=1,
        )
        state_manager.save_work_state(state2)

        # Check for backup files (work_state.json.bak, .bak1, .bak2)
        backup_dir = temp_state_file.parent
        backup_files = list(backup_dir.glob(f"{temp_state_file.name}.bak*"))

        # Should have at least the main file and one backup
        assert len(backup_files) >= 1

    def test_increment_streak(self, state_manager):
        """Test streak increment logic."""
        current_streak = 3
        new_streak = state_manager.increment_streak(current_streak)

        assert new_streak == 4

    def test_increment_streak_from_zero(self, state_manager):
        """Test incrementing streak from zero."""
        current_streak = 0
        new_streak = state_manager.increment_streak(current_streak)

        assert new_streak == 1

    def test_reset_streak(self, state_manager):
        """Test streak reset logic."""
        new_streak = state_manager.reset_streak()

        assert new_streak == 0

    def test_determine_productive_session_all_criteria_met(self, state_manager):
        """Test productive session with all criteria met."""
        is_productive = state_manager.determine_productive_session(
            tracking_minutes=45,  # >= 30 min required
            focus_score=75,  # >= 50 required
            completed_tasks=["Task 1", "Task 2"],  # >= 1 task required
        )

        assert is_productive is True

    def test_determine_productive_session_insufficient_time(self, state_manager):
        """Test session not productive due to insufficient tracking time."""
        is_productive = state_manager.determine_productive_session(
            tracking_minutes=15,  # < 30 min
            focus_score=90,
            completed_tasks=["Task 1"],
        )

        assert is_productive is False

    def test_determine_productive_session_low_focus_score(self, state_manager):
        """Test session not productive due to low focus score."""
        is_productive = state_manager.determine_productive_session(
            tracking_minutes=60,
            focus_score=30,  # < 50
            completed_tasks=["Task 1"],
        )

        assert is_productive is False

    def test_determine_productive_session_no_completed_tasks(self, state_manager):
        """Test session not productive due to no completed tasks."""
        is_productive = state_manager.determine_productive_session(
            tracking_minutes=60,
            focus_score=80,
            completed_tasks=[],  # No tasks
        )

        assert is_productive is False

    def test_determine_productive_session_without_focus_score(self, state_manager):
        """Test productive session determination when focus score is None."""
        # Should still be productive if time >= 30 min and has tasks
        is_productive = state_manager.determine_productive_session(
            tracking_minutes=45,
            focus_score=None,  # No focus score
            completed_tasks=["Task 1"],
        )

        assert is_productive is True

    def test_determine_productive_session_boundary_values(self, state_manager):
        """Test productive session with boundary values."""
        # Exactly 30 minutes, score 50, 1 task (all at minimum)
        is_productive = state_manager.determine_productive_session(
            tracking_minutes=30,  # Exactly minimum
            focus_score=50,  # Exactly minimum
            completed_tasks=["Task 1"],  # Exactly 1 task
        )

        assert is_productive is True

    def test_update_streak_if_productive_increments(self, state_manager):
        """Test that productive session increments streak."""
        work_state = WorkState(
            session_summary="Previous session",
            completed_tasks=[],
            timestamp="2024-01-28T10:00:00",
            streak_count=3,
            last_productive_session="2024-01-27T15:00:00",
        )

        session_timestamp = "2024-01-28T11:00:00"
        updated_state = state_manager.update_streak_if_productive(
            work_state, is_productive=True, session_timestamp=session_timestamp
        )

        assert updated_state.streak_count == 4
        assert updated_state.last_productive_session == session_timestamp

    def test_update_streak_if_productive_from_zero(self, state_manager):
        """Test incrementing streak from zero."""
        work_state = WorkState.create_empty()  # streak_count = 0

        session_timestamp = "2024-01-28T11:00:00"
        updated_state = state_manager.update_streak_if_productive(
            work_state, is_productive=True, session_timestamp=session_timestamp
        )

        assert updated_state.streak_count == 1
        assert updated_state.last_productive_session == session_timestamp

    def test_update_streak_if_not_productive_no_change(self, state_manager):
        """Test that non-productive session doesn't increment streak."""
        work_state = WorkState(
            session_summary="Previous session",
            completed_tasks=[],
            timestamp="2024-01-28T10:00:00",
            streak_count=5,
            last_productive_session="2024-01-27T15:00:00",
        )

        session_timestamp = "2024-01-28T11:00:00"
        updated_state = state_manager.update_streak_if_productive(
            work_state, is_productive=False, session_timestamp=session_timestamp
        )

        # Streak should not change
        assert updated_state.streak_count == 5
        # Last productive session should not be updated
        assert updated_state.last_productive_session == "2024-01-27T15:00:00"

    def test_update_streak_preserves_other_fields(self, state_manager):
        """Test that updating streak preserves other work state fields."""
        work_state = WorkState(
            session_summary="Original summary",
            completed_tasks=["Task A"],
            timestamp="2024-01-28T10:00:00",
            streak_count=2,
            focus_score=70,
            total_tracking_minutes=45,
        )

        session_timestamp = "2024-01-28T11:00:00"
        updated_state = state_manager.update_streak_if_productive(
            work_state, is_productive=True, session_timestamp=session_timestamp
        )

        # Other fields should be preserved
        assert updated_state.session_summary == "Original summary"
        assert updated_state.completed_tasks == ["Task A"]
        assert updated_state.focus_score == 70
        assert updated_state.total_tracking_minutes == 45

    def test_backup_recovery_when_corrupted(self, state_manager, temp_state_file):
        """Test behavior when main file is corrupted (no auto-recovery)."""
        from utils.file_handler import DataCorruptionError

        # Create initial valid state
        original_state = WorkState(
            session_summary="Original session",
            completed_tasks=["Task 1"],
            timestamp="2024-01-28T10:00:00",
            streak_count=3,
        )
        state_manager.save_work_state(original_state)

        # Corrupt the main file
        temp_state_file.write_text("{corrupted data")

        # Currently, file_handler does NOT auto-recover from backups
        # It raises DataCorruptionError for corrupted files
        with pytest.raises(DataCorruptionError, match="Corrupted JSON file"):
            state_manager.load_work_state()

        # Note: Backup files are created during write_json operations
        # Future enhancement could implement automatic backup recovery

    def test_multiple_save_and_load_cycles(self, state_manager):
        """Test multiple save/load cycles maintain data integrity."""
        states = [
            WorkState(
                session_summary=f"Session {i}",
                completed_tasks=[f"Task {i}"],
                timestamp=f"2024-01-28T{10+i}:00:00",
                streak_count=i,
            )
            for i in range(5)
        ]

        # Save and load each state
        for state in states:
            state_manager.save_work_state(state)
            loaded = state_manager.load_work_state()
            assert loaded.session_summary == state.session_summary
            assert loaded.streak_count == state.streak_count
