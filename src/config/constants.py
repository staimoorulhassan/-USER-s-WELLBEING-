"""Application constants for Wellbeing desktop tracker."""

from pathlib import Path

# =============================================================================
# File Paths
# =============================================================================

HOME_DIR = Path.home()
WELLBEING_DIR = HOME_DIR / ".wellbeing"
DATA_DIR = WELLBEING_DIR

PROFILE_FILE = DATA_DIR / "profile.json"
LOGS_FILE = DATA_DIR / "logs.json"
WORK_STATE_FILE = DATA_DIR / "work_state.json"

# =============================================================================
# Polling Configuration
# =============================================================================

POLLING_INTERVAL_SECONDS = 5
MAX_LIVE_FEED_ENTRIES = 20

# =============================================================================
# AI Service Timeouts
# =============================================================================

AI_TIMEOUT_MANUAL_SECONDS = 30
AI_TIMEOUT_SHUTDOWN_SECONDS = 5

# =============================================================================
# Browser Suffix Patterns
# =============================================================================

BROWSER_SUFFIXES = [
    r" - Google Chrome$",
    r" - Mozilla Firefox$",
    r" - Microsoft Edge$",
    r" - Brave$",
    r" - Opera$",
    r" - Vivaldi$",
]

# =============================================================================
# Data Management
# =============================================================================

LOG_SIZE_WARNING_MB = 50
LOG_SIZE_LIMIT_MB = 100
BACKUP_COUNT = 3

# =============================================================================
# Tracking Thresholds
# =============================================================================

MIN_PRODUCTIVE_SESSION_MINUTES = 30
MIN_FOCUS_SCORE = 50

# =============================================================================
# Notification Configuration
# =============================================================================

TASK_DETECTION_INTERVAL_MINUTES = 10
NOTIFICATION_AUTO_DISMISS_SECONDS = 5

# =============================================================================
# Environment Variables
# =============================================================================

ENV_GEMINI_API_KEY = "GEMINI_API_KEY"
ENV_ZAI_API_KEY = "ZAI_API_KEY"
ENV_POLLINATIONS_API_KEY = "POLLINATIONS_API_KEY"
ENV_AI_PROVIDER = "AI_PROVIDER"  # "gemini", "zai", or "pollinations"


