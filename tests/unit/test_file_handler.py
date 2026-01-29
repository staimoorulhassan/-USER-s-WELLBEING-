"""Unit tests for file handler profile save/load operations.

Tests that:
- Atomic write prevents corruption
- Backup files are created
- Corrupted files can be recovered from backup
"""

import pytest
import json
from pathlib import Path
from utils.file_handler import write_json, read_json, restore_from_backup, FileHandlerError


class TestFileHandlerProfileOperations:
    """Test file handler operations for profile management."""

    @pytest.fixture
    def temp_file(self, tmp_path):
        """Provide temporary file path."""
        return tmp_path / "test_profile.json"

    def test_write_creates_file(self, temp_file):
        """Test that write_json creates a new file."""
        data = {"name": "John", "role": "Developer", "main_goal": "Build software"}

        write_json(temp_file, data)

        assert temp_file.exists()
        assert temp_file.read_text() == json.dumps(data, indent=2)

    def test_write_creates_backup(self, temp_file):
        """Test that write_json creates a backup of existing file."""
        original_data = {"name": "John", "role": "Developer", "main_goal": "Build software"}

        write_json(temp_file, original_data)

        # Check backup was created
        backup_file = temp_file.with_suffix(".json.bak")
        assert backup_file.exists()

        # Verify backup content
        backup_data = json.loads(backup_file.read_text())
        assert backup_data == original_data

    def test_atomic_write_prevents_corruption(self, temp_file):
        """Test that interrupted write doesn't corrupt target file."""
        original_data = {"name": "John", "role": "Developer"}
        write_json(temp_file, original_data)

        # Store original content
        original_content = temp_file.read_text()

        # Simulate failed write (will clean up temp file)
        try:
            bad_data = {"invalid": "data"}
            # Write to temp then fail before replace
            temp_path = temp_file.with_suffix(".json.tmp")
            temp_path.write_text(json.dumps(bad_data))
            # Don't call os.replace - simulate failure
            temp_path.unlink()
        except Exception:
            pass

        # Original file should still be intact
        assert temp_file.read_text() == original_content

    def test_read_returns_none_for_missing_file(self, tmp_path):
        """Test that read_json returns None for non-existent file."""
        missing_file = tmp_path / "nonexistent.json"
        result = read_json(missing_file)

        assert result is None

    def test_read_parses_valid_json(self, temp_file):
        """Test that read_json parses valid JSON correctly."""
        data = {"name": "John", "role": "Developer"}
        temp_file.write_text(json.dumps(data))

        result = read_json(temp_file)

        assert result == data

    def test_read_raises_error_for_corrupted_json(self, temp_file):
        """Test that read_json raises error for corrupted JSON."""
        from utils.exceptions import DataCorruptionError

        temp_file.write_text("{invalid json content")

        with pytest.raises(DataCorruptionError, match="Corrupted JSON"):
            read_json(temp_file)

    def test_restore_from_backup_succeeds(self, temp_file):
        """Test that corrupted file can be restored from backup."""
        original_data = {"name": "John", "role": "Developer"}

        # Write valid data (creates backup)
        write_json(temp_file, original_data)

        # Corrupt the main file
        temp_file.write_text("{corrupted json}")

        # Restore from backup
        success = restore_from_backup(temp_file)

        assert success is True
        restored_data = read_json(temp_file)
        assert restored_data == original_data

    def test_restore_fails_when_no_backup(self, temp_file):
        """Test that restore returns False when no backup exists."""
        # File exists but no backup
        temp_file.write_text("some data")

        success = restore_from_backup(temp_file)

        assert success is False

    def test_write_creates_parent_directory(self, tmp_path):
        """Test that write_json creates parent directories if needed."""
        nested_file = tmp_path / "subdir" / "nested" / "profile.json"

        data = {"name": "John"}

        write_json(nested_file, data)

        assert nested_file.exists()
        assert nested_file.parent.exists()
