# Implementation Plan: User's Wellbeing - Desktop Tracking Application

**Branch**: `001-wellbeing-mvp` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-wellbeing-mvp/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Desktop wellbeing tracking application that monitors user window activity, provides real-time focus metrics, and delivers AI-powered productivity insights. Features include onboarding, background window tracking (5s polling), AI-generated focus scores, daily summaries, task accomplishment celebrations, work state persistence across sessions, and system event interception (shutdown/restart/sleep). Uses Python with CustomTkinter for UI, pywin32 for window tracking, Google Gemini API for AI analysis, and local JSON storage for privacy.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: CustomTkinter (UI), pywin32 (window tracking), google-generativeai (Gemini API), threading, json, pathlib
**Storage**: Local JSON files (profile.json, logs.json, work_state.json)
**Testing**: pytest with pytest-qt for UI testing, unittest.mock for AI service mocking
**Target Platform**: Windows 10/11 (pywin32 specific), expandable to macOS/Linux via platform-specific window APIs
**Project Type**: Single desktop application
**Performance Goals**: 5-second polling interval, <10s UI updates, <15s AI summary generation, 8-hour continuous tracking <500MB memory
**Constraints**: Must work offline (except AI features), single instance enforcement, graceful AI service degradation, adaptive timeouts (5s shutdown, 30s manual)
**Scale/Scope**: Single-user desktop app, ~10-15 UI screens/views, 5 core entities, ~2000 LOC estimated

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: No project constitution exists yet (.specify/memory/constitution.md is a template). The following quality gates are established based on industry best practices for desktop applications:

**Quality Gates**:
- ✅ **Privacy-First Design**: All user data stored locally, no telemetry without explicit consent
- ✅ **Single Instance Architecture**: Prevents data corruption, simplifies state management
- ✅ **Graceful Degradation**: Application functions without AI service; offline-capable core features
- ✅ **Testability Requirements**: All features independently testable, AI service mocked in tests
- ✅ **Observability**: Structured logging for debugging, user-visible error messages
- ✅ **Resource Management**: Memory leak prevention, proper thread lifecycle management
- ✅ **Data Integrity**: Atomic file writes, backup/recovery mechanisms for critical data

**All gates PASSED** - proceeding to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
wellbeing/
├── src/
│   ├── __init__.py
│   ├── main.py                      # Application entry point
│   ├── models/                      # Data models
│   │   ├── __init__.py
│   │   ├── profile.py               # User Profile entity
│   │   ├── activity_log.py          # Window Activity Log entity
│   │   ├── work_state.py            # Work State entity
│   │   └── ai_models.py             # AI request/response models
│   ├── services/                    # Business logic
│   │   ├── __init__.py
│   │   ├── tracker.py               # Window tracking engine
│   │   ├── ai_service.py            # Gemini API integration
│   │   ├── state_manager.py         # Work state persistence
│   │   ├── instance_manager.py      # Single instance enforcement
│   │   └── event_interceptor.py     # Shutdown/sleep event handling
│   ├── ui/                          # CustomTkinter UI components
│   │   ├── __init__.py
│   │   ├── main_window.py           # Primary application window
│   │   ├── onboarding.py            # Welcome screen
│   │   ├── dashboard.py             # Main dashboard with tracking controls
│   │   ├── settings.py              # Options/settings menu
│   └── notifications.py             # Toast/popup notifications
│   ├── utils/                       # Utilities
│   │   ├── __init__.py
│   │   ├── file_handler.py          # Atomic JSON file operations
│   │   └── browser_filters.py       # Browser suffix filtering
│   └── config/                      # Configuration
│       ├── __init__.py
│       └── constants.py             # Application constants
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # pytest fixtures
│   ├── unit/                        # Unit tests
│   │   ├── test_models.py
│   │   ├── test_tracker.py
│   │   ├── test_ai_service.py
│   │   └── test_file_handler.py
│   ├── integration/                 # Integration tests
│   │   ├── test_tracking_flow.py
│   │   └── test_state_persistence.py
│   └── fixtures/                    # Test data
│       ├── test_profile.json
│       └── test_logs.json
├── data/                            # Runtime data (gitignored)
│   ├── profile.json                 # Created at runtime
│   ├── logs.json                    # Created at runtime
│   └── work_state.json              # Created at runtime
├── docs/                            # Additional documentation
├── .env.example                     # API key template
├── .gitignore
├── pyproject.toml                   # Project dependencies
├── main.py                          # Entry point symlink to src/main.py
└── README.md
```

**Structure Decision**: Single-project Python desktop application structure following standard Python packaging conventions. Separation of concerns with distinct layers for models (data), services (business logic), and UI (presentation). Testing organized by level (unit/integration) with fixtures for reproducible tests. Runtime data stored in `data/` directory (gitignored).

**No complexity violations** - architecture is straightforward and appropriate for scope.

---

## Phase 0: Research & Technical Decisions

See [research.md](./research.md) for detailed technical decisions and rationale.

---

## Phase 1: Design Artifacts

See [data-model.md](./data-model.md) for entity definitions and [quickstart.md](./quickstart.md) for development setup.

---

## Phase 2: Implementation Tasks

See [tasks.md](./tasks.md) - generated by `/sp.tasks` command (not created by `/sp.plan`).
