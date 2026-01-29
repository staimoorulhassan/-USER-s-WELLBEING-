# Data Model

**Feature**: User's Wellbeing - Desktop Tracking Application
**Date**: 2025-01-27
**Status**: Complete

## Overview

This document defines the data entities, their attributes, relationships, validation rules, and persistence mechanisms for the wellbeing tracking application.

---

## Entity Definitions

### 1. User Profile

**Filename**: `profile.json`
**Location**: `~/.wellbeing/profile.json` (Windows: `%USERPROFILE%\.wellbeing\profile.json`)
**Cardinality**: One per application installation

```json
{
  "name": "string (required, min 1 char, max 100 chars)",
  "role": "string (required, min 1 char, max 50 chars)",
  "main_goal": "string (required, min 1 char, max 500 chars)",
  "created_at": "ISO 8601 datetime (auto-generated)",
  "last_updated": "ISO 8601 datetime (auto-updated on save)"
}
```

**Validation Rules**:
- `name`: Non-empty, trimmed, max 100 characters, no control characters
- `role`: Non-empty, trimmed, max 50 characters
- `main_goal`: Non-empty, trimmed, max 500 characters
- `created_at`: Auto-generated on first launch, immutable
- `last_updated`: Automatically updated on every save operation

**Example**:
```json
{
  "name": "Alice Johnson",
  "role": "Software Developer",
  "main_goal": "Complete the machine learning course and build 2 projects",
  "created_at": "2025-01-27T10:30:00Z",
  "last_updated": "2025-01-27T10:30:00Z"
}
```

**State Transitions**: None (profile is created once and updated)

---

### 2. Window Activity Log

**Filename**: `logs.json`
**Location**: `~/.wellbeing/logs.json`
**Cardinality**: Append-only collection, unlimited entries (manual cleanup)

```json
{
  "entries": [
    {
      "timestamp": "ISO 8601 datetime (required, UTC)",
      "window_title": "string (required, filtered of browser suffixes)",
      "raw_window_title": "string (required, original unfiltered)",
      "application": "string (derived, executable name if available)",
      "duration_seconds": "integer (optional, computed for consecutive same-window events)"
    }
  ],
  "metadata": {
    "version": "string (format version)",
    "total_entries": "integer (auto-calculated)",
    "size_bytes": "integer (auto-calculated)"
  }
}
```

**Validation Rules**:
- `timestamp`: Required, ISO 8601 format, UTC timezone, monotonically increasing
- `window_title`: Non-empty after filtering, max 255 characters
- `raw_window_title`: Non-empty (original may be empty), max 255 characters
- `application`: Optional, extracted from window title or process info
- `duration_seconds`: Computed field, >= 0

**Browser Suffix Filtering**:
Regex patterns to remove:
```python
BROWSER_SUFFIXES = [
    r" - Google Chrome$",
    r" - Mozilla Firefox$",
    r" - Microsoft Edge$",
    r" - Brave$",
    r" - Opera$",
    r" - Vivaldi$"
]
```

**Example**:
```json
{
  "entries": [
    {
      "timestamp": "2025-01-27T14:35:00Z",
      "window_title": "Visual Studio Code",
      "raw_window_title": "Visual Studio Code - main.py - Wellbeing Tracker",
      "application": "code.exe",
      "duration_seconds": null
    },
    {
      "timestamp": "2025-01-27T14:35:05Z",
      "window_title": "GitHub - Pull Request #123",
      "raw_window_title": "GitHub - Pull Request #123 - Google Chrome",
      "application": "chrome.exe",
      "duration_seconds": null
    }
  ],
  "metadata": {
    "version": "1.0",
    "total_entries": 2,
    "size_bytes": 512
  }
}
```

**State Transitions**: Append-only (entries never modified or deleted, except manual cleanup)

---

### 3. Work State

**Filename**: `work_state.json`
**Location**: `~/.wellbeing/work_state.json`
**Cardinality**: One per application (overwritten on session end)

```json
{
  "session_summary": "string (required, AI-generated or user-provided)",
  "completed_tasks": [
    "string (task description, max 200 chars each)"
  ],
  "timestamp": "ISO 8601 datetime (required, session end time)",
  "streak_count": "integer (required, consecutive productive sessions)",
  "last_productive_session": "ISO 8601 datetime (nullable)",
  "focus_score": "float (nullable, 0-100 scale)",
  "total_tracking_minutes": "integer (required, >=0)"
}
```

**Validation Rules**:
- `session_summary`: Non-empty, max 1000 characters
- `completed_tasks`: Array of strings, each max 200 characters, max 20 tasks
- `timestamp`: Required, ISO 8601 format
- `streak_count`: Integer >= 0, incremented on productive sessions, reset on missed days
- `last_productive_session`: ISO 8601 datetime or null
- `focus_score`: Float 0-100 if present, null if not calculated
- `total_tracking_minutes`: Integer >= 0

**Productive Session Definition**:
- Total tracking time >= 30 minutes
- Focus score >= 50 (if calculated)
- At least one task accomplishment detected

**Example**:
```json
{
  "session_summary": "Great focus on Python development. Completed main.py implementation and tracked 3 bugs.",
  "completed_tasks": [
    "Implemented window tracking service",
    "Fixed JSON file corruption bug",
    "Added browser suffix filtering"
  ],
  "timestamp": "2025-01-27T18:00:00Z",
  "streak_count": 5,
  "last_productive_session": "2025-01-27T18:00:00Z",
  "focus_score": 82.5,
  "total_tracking_minutes": 240
}
```

**State Transitions**:
- Created on session end (shutdown, manual stop, or crash recovery)
- Overwritten on subsequent session end (previous state backed up to work_state.json.bak)

---

### 4. Daily Summary (Transient)

**Filename**: None (in-memory, optionally saved by user)
**Persistence**: User explicitly saves to file (e.g., "Export Summary" button)

```json
{
  "summary_text": "string (required, AI-generated)",
  "productivity_patterns": [
    "string (insight about work patterns)"
  ],
  "time_distribution": {
    "category": "string (e.g., 'Development', 'Research')",
    "minutes": "integer (time spent)"
  },
  "goal_alignment": "string (assessment of goal progress)",
  "recommendations": [
    "string (actionable suggestions)"
  ],
  "generated_at": "ISO 8601 datetime"
}
```

**Validation Rules**:
- `summary_text`: Non-empty, max 2000 characters
- `productivity_patterns`: Array of strings, max 10 patterns, each max 200 characters
- `time_distribution`: Dictionary, max 10 categories, values >= 0
- `goal_alignment`: String, max 500 characters
- `recommendations`: Array of strings, max 5 recommendations, each max 200 characters

**Example**:
```json
{
  "summary_text": "You had a highly productive session focused on Python development. Your most active window was Visual Studio Code for 65% of tracked time. Task accomplishments detected at 2:15 PM (implemented tracker service) and 4:30 PM (fixed JSON bug).",
  "productivity_patterns": [
    "Peak focus hours: 2 PM - 5 PM",
    "Longest uninterrupted focus session: 90 minutes",
    "Most used applications: VS Code (65%), Chrome (20%), Terminal (10%)"
  ],
  "time_distribution": {
    "Development": 156,
    "Research": 48,
    "Communication": 36
  },
  "goal_alignment": "Good progress on machine learning course goal. Completed 2 projects as planned. Consider dedicating more time to course videos.",
  "recommendations": [
    "Take breaks every 90 minutes to maintain focus",
    "Schedule deep work sessions during 2-5 PM peak hours",
    "Limit browser usage during development time"
  ],
  "generated_at": "2025-01-27T18:05:00Z"
}
```

**State Transitions**: Generated on-demand via AI service, not persisted unless user exports

---

## Relationships

```
User Profile (1)
    ↓
Window Activity Log (many entries)
    ↓
Work State (aggregates from logs)
    ↓
Daily Summary (derived from logs + profile + work state)
```

**Relationship Rules**:
1. Window Activity Log entries reference User Profile context (goals, role) for AI analysis
2. Work State aggregates Window Activity Log entries (total time, streak)
3. Daily Summary combines User Profile + Window Activity Log + (optionally) Work State

---

## Data Integrity Constraints

### Atomic Writes

All JSON files use atomic write pattern to prevent corruption:

```python
def atomic_write(filepath: str, data: dict) -> None:
    """Write data to file atomically."""
    import tempfile
    import os

    # Write to temporary file
    fd, temp_path = tempfile.mkstemp(
        dir=os.path.dirname(filepath),
        prefix=os.path.basename(filepath) + '.tmp'
    )
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

        # Atomic replace (POSIX and Windows)
        os.replace(temp_path, filepath)
    except Exception:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise
```

### Backup Strategy

Retain last 3 versions of modified files:

```
profile.json (current)
profile.json.bak (1 backup)
profile.json.bak.1 (2 backups ago)
profile.json.bak.2 (3 backups ago)
```

Rotation: On save, delete `.bak.2`, rename `.bak.1` → `.bak.2`, `.bak` → `.bak.1`, current → `.bak`

### File Locking

Use advisory file locking to prevent concurrent writes:

```python
import fcntl  # Linux/macOS
import portalocker  # Cross-platform alternative

# Windows: Use msvcrt.locking() or portalocker
# POSIX: Use fcntl.flock()
```

---

## Data Migration

### Version Schema

Include `metadata.version` field in all JSON files for future migrations:

```json
{
  "data": { ... },
  "metadata": {
    "version": "1.0",
    "format_version": "1.0"
  }
}
```

### Migration Strategy

On application launch:

1. Read profile.json, check `metadata.version`
2. If version < current, run migration script:
   - Backup existing file to `profile.json.v{old_version}`
   - Apply transformation (add/remove fields, change types)
   - Update `metadata.version` to current
   - Write atomically
3. If migration fails, restore from backup and log error

---

## Privacy & Security

### Sensitive Data Handling

**Never log**:
- Window titles (may contain document names, URLs, PII)
- User names (except in profile.json which is user-controlled)
- API keys (only in memory or environment variables)

**Always sanitize**:
- Window titles before sending to AI (remove PII patterns: emails, phone numbers, SSNs)
- Log files (remove paths, keep only metadata)

### API Key Storage

```python
# Option 1: Environment variable (recommended)
import os
api_key = os.getenv("GEMINI_API_KEY")

# Option 2: Windows Credential Manager (more secure)
import keyring
keyring.set_password("wellbeing-app", "gemini-api", api_key)
api_key = keyring.get_password("wellbeing-app", "gemini-api")
```

Never hardcode API keys in source code.

---

## Performance Considerations

### File Size Limits

- `profile.json`: < 10 KB (negligible)
- `logs.json`: Monitor size, warn at 50 MB, prompt cleanup at 100 MB
- `work_state.json`: < 50 KB (negligible)

### Loading Performance

- Lazy-load logs.json (don't load entire file on startup, use streaming)
- Memory-mapped file for large logs (>50 MB): `mmap.mmap()`
- Index last N entries (e.g., last 1000) for live feed display

### Write Optimization

- Batch log entries (write every 10 entries or every 5 minutes)
- Buffer in memory, flush to disk periodically
- Use compact JSON (no indentation) for logs.json to reduce size

---

## Summary

The data model prioritizes simplicity (JSON files), privacy (local-only storage), and integrity (atomic writes, backups). All entities are validated and versioned for future migrations. Relationships between entities support AI-generated insights while maintaining user control over data.

**Next Step**: See [quickstart.md](./quickstart.md) for implementation setup and development workflow.
