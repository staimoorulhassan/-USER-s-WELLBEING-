"""Data directory initialization and path utilities.

Ensures ~/.wellbeing/ directory structure exists and is accessible.
"""

import logging
from pathlib import Path

from config.constants import (
    WELLBEING_DIR,
    DATA_DIR,
    PROFILE_FILE,
    LOGS_FILE,
    WORK_STATE_FILE,
)

logger = logging.getLogger(__name__)


def initialize_data_directory() -> bool:
    """Create ~/.wellbeing/ directory structure if it doesn't exist.

    Creates the main data directory and any needed subdirectories.
    Handles Windows path special cases.

    Returns:
        True if directory exists or was created successfully
        False if directory creation failed
    """
    try:
        WELLBEING_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Data directory ready: {WELLBEING_DIR}")
        return True
    except OSError as e:
        logger.error(f"Failed to create data directory {WELLBEING_DIR}: {e}")
        return False


def get_all_data_paths() -> dict[str, Path]:
    """Get all data file paths used by the application.

    Returns:
        Dictionary mapping file names to their paths
    """
    return {
        "profile": PROFILE_FILE,
        "logs": LOGS_FILE,
        "work_state": WORK_STATE_FILE,
    }


def verify_data_directory() -> bool:
    """Verify data directory exists and is writable.

    Returns:
        True if directory is accessible and writable
    """
    if not WELLBEING_DIR.exists():
        logger.warning(f"Data directory does not exist: {WELLBEING_DIR}")
        return False

    # Test write permissions
    test_file = WELLBEING_DIR / ".write_test"
    try:
        test_file.touch()
        test_file.unlink()
        return True
    except OSError as e:
        logger.error(f"Data directory not writable: {e}")
        return False
