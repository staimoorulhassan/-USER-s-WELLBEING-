# Tasks: User's Wellbeing - Desktop Tracking Application

**Input**: Design documents from `/specs/001-wellbeing-mvp/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test tasks are included to ensure TDD approach and quality standards.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single desktop application structure per plan.md:
- Source: `src/` with models/, services/, ui/, utils/, config/ subdirectories
- Tests: `tests/unit/`, `tests/integration/`, `tests/fixtures/`
- Runtime data: `data/` (gitignored)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure per implementation plan (src/, tests/, data/, docs/)
- [X] T002 Initialize Python project with pyproject.toml and dependencies (CustomTkinter, pywin32, google-generativeai, pytest, pytest-qt)
- [X] T003 [P] Create .gitignore with Python patterns (__pycache__/, *.pyc, .venv/, venv/, data/, .env)
- [X] T004 [P] Create .env.example template with GEMINI_API_KEY placeholder
- [X] T005 [P] Create pytest configuration in pyproject.toml or pytest.ini (test paths, mock paths, coverage settings)
- [X] T006 [P] Create README.md with project description, setup instructions, and prerequisites
- [X] T007 Create application constants file in src/config/constants.py (polling interval, timeouts, file paths, browser suffixes)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Implement atomic JSON file handler in utils/file_handler.py (read_json, write_json, restore_from_backup, atomic write pattern)
- [X] T009 [P] Create base exception classes in utils/exceptions.py (WellbeingError, TrackerError, AIServiceError, DataCorruptionError, InstanceError)
- [X] T010 [P] Setup structured logging configuration in utils/logger.py (RotatingFileHandler, log levels, formatters)
- [X] T011 [P] Create browser suffix filter utility in utils/browser_filters.py (filter method, 6 default patterns, add_custom_suffix)
- [X] T012 [P] Implement data directory initialization in utils/path_helper.py (create ~/.wellbeing/ if missing, handle Windows paths)
- [X] T013 [P] Create base UI component in ui/main_window.py (CustomTkinter.CTkToplevel skeleton, window configuration)
- [X] T014 Create main application entry point in src/main.py (argument parsing, logging setup, UI initialization)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - First-Time User Onboarding (Priority: P1) 🎯 MVP

**Goal**: Enable users to create their profile on first launch

**Independent Test**: Launch application, complete onboarding form, verify profile.json created and dashboard shown

### Tests for User Story 1

- [X] T015 [P] [US1] Unit test for Profile model validation in tests/unit/test_profile.py (empty fields, max lengths, auto-generated timestamps)
- [X] T016 [P] [US1] Integration test for onboarding flow in tests/integration/test_onboarding.py (first launch detection, form validation, profile save, dashboard transition)
- [X] T017 [P] [US1] Unit test for file handler profile save/load in tests/unit/test_file_handler.py (atomic write, backup creation, corrupted recovery)

### Implementation for User Story 1

- [X] T018 [P] [US1] Create UserProfile model in models/profile.py (name, role, main_goal, created_at, last_updated, validation methods)
- [X] T019 [P] [US1] Create onboarding UI frame in ui/onboarding.py (CustomTkinter.CTkFrame, form fields, submit button, validation messages)
- [X] T020 [US1] Implement profile load logic in services/profile_service.py (detect existing profile.json, load and validate, return profile or None)
- [X] T021 [US1] Implement profile save logic in services/profile_service.py (validate input, add timestamps, save via file_handler, create backup)
- [X] T022 [US1] Wire onboarding UI to main window in ui/main_window.py (show onboarding if no profile, hide if profile exists, transition to dashboard on submit)
- [X] T023 [US1] Add form validation feedback in ui/onboarding.py (real-time validation, error messages, disable submit until valid)
- [X] T024 [US1] Add logging for onboarding operations (profile created, profile loaded, validation errors)

**Checkpoint**: User Story 1 complete - users can onboard and see empty dashboard

---

## Phase 4: User Story 2 - Live Activity Tracking (Priority: P1) 🎯 MVP

**Goal**: Enable background window tracking with real-time live feed display

**Independent Test**: Start tracking, switch windows, verify live feed updates within 10 seconds

### Tests for User Story 2

- [X] T025 [P] [US2] Unit test for ActivityLog model in tests/unit/test_activity_log.py (timestamp validation, browser suffix filtering, required fields)
- [X] T026 [P] [US2] Unit test for tracker service in tests/unit/test_tracker.py (start/stop tracking, polling logic, window title capture)
- [X] T027 [P] [US2] Unit test for browser filter in tests/unit/test_browser_filters.py (suffix removal patterns, empty title handling, special characters)
- [X] T028 [P] [US2] Integration test for tracking flow in tests/integration/test_tracking_flow.py (start tracker, window switches, log file updates, background thread)

### Implementation for User Story 2

- [X] T029 [P] [US2] Create ActivityLogEntry model in models/activity_log.py (timestamp, window_title, raw_window_title, application, duration_seconds)
- [X] T030 [P] [US2] Create logs.json file structure handler in utils/log_handler.py (initialize entries array, append entry, update metadata, manage file size)
- [X] T031 [US2] Implement tracker service in services/tracker.py (background threading.Thread, 5-second polling, pywin32 GetForegroundWindow/GetWindowText, browser filter integration)
- [X] T032 [US2] Implement polling loop with graceful exception handling in services/tracker.py (catch Windows exceptions, empty titles, handle application crashes)
- [X] T033 [US2] Create dashboard UI frame in ui/dashboard.py (CustomTkinter.CTkFrame, layout structure, widgets placeholder)
- [X] T034 [US2] Implement Start/Stop tracking buttons in ui/dashboard.py (button widgets, tracker service integration, status indicator, button state management)
- [X] T035 [US2] Create Live Feed UI component in ui/dashboard.py (scrollable list, recent entries display, refresh mechanism, timestamp formatting)
- [X] T036 [US2] Implement thread-safe UI updates for live feed in services/tracker.py (queue.Queue or root.after, communicate window title changes to UI thread)
- [X] T037 [US2] Add tracking state persistence across UI minimization in services/tracker.py (daemon=True thread, continue polling when UI hidden)
- [X] T038 [US2] Add logging for tracker operations (tracking started/stopped, polling errors, window titles captured, log file writes)

**Checkpoint**: User Stories 1 & 2 complete - users can onboard, track activity, see live feed

---

## Phase 5: User Story 3 - Focus Score Dashboard (Priority: P2)

**Goal**: Display AI-calculated focus score on dashboard

**Independent Test**: Track activity for 5+ minutes, verify focus score displayed and updates

### Tests for User Story 3

- [X] T039 [P] [US3] Unit test for AI service focus score calculation in tests/unit/test_ai_service.py (mock Gemini API, test prompt generation, test score parsing)
- [X] T040 [P] [US3] Integration test for focus score flow in tests/integration/test_focus_score.py (track activity, calculate score, update dashboard, handle AI errors)

### Implementation for User Story 3

- [X] T041 [P] [US3] Create FocusScore model in models/ai_models.py (numeric value 0-100, calculated_at, activity_summary)
- [X] T042 [US3] Implement AI service client in services/ai_service.py (Google Gemini API integration, calculate_focus_score method, 30-second timeout, retry logic)
- [X] T043 [US3] Create focus score prompt generator in services/ai_service.py (format activity logs for AI, include user goals/role context, handle edge cases)
- [X] T044 [US3] Implement focus score display widget in ui/dashboard.py (large numeric display, color coding, trend indicator, N/A state for no data)
- [X] T045 [US3] Add focus score refresh logic in services/ai_service.py (trigger calculation on tracking intervals, cache score, update dashboard)
- [X] T046 [US3] Implement graceful degradation for AI failures in services/ai_service.py (show cached score or N/A, log error, user-friendly error message)
- [X] T047 [US3] Add focus score update trigger in services/tracker.py (request AI calculation every 5 minutes or on significant window pattern changes)

**Checkpoint**: User Stories 1-3 complete - core tracking and insights functional

---

## Phase 6: User Story 4 - AI-Powered Daily Summary (Priority: P2)

**Goal**: Generate intelligent daily summary from activity logs

**Independent Test**: Track activity, click "Stop & Summarize", verify summary displayed with insights

### Tests for User Story 4

- [X] T048 [P] [US4] Unit test for daily summary generation in tests/unit/test_ai_service.py (mock Gemini API, test batch log formatting, test summary parsing)
- [X] T049 [P] [US4] Integration test for summary flow in tests/integration/test_summary.py (track activity, generate summary, display insights, handle empty logs)

### Implementation for User Story 4

- [X] T050 [P] [US4] Create DailySummary model in models/ai_models.py (summary_text, productivity_patterns list, time_distribution dict, goal_alignment, recommendations list, generated_at)
- [X] T051 [US4] Implement daily summary generation in services/ai_service.py (send all logs to Gemini API, parse response, handle adaptive timeout: 30s manual, 5s shutdown)
- [X] T052 [US4] Create "Stop & Summarize" button in ui/dashboard.py (button widget, AI service integration, loading indicator)
- [X] T053 [US4] Create summary display dialog in ui/notifications.py (modal window, scrollable text, productivity patterns, time distribution, recommendations)
- [X] T054 [US4] Implement summary error handling in services/ai_service.py (translate 429 rate limit, timeout, server error to user-friendly messages, preserve local logs)
- [X] T055 [US4] Add empty logs handling in services/ai_service.py (detect no activity logs, show informative message, skip API call)
- [X] T056 [US4] Add logging for summary operations (API requests, responses, errors, user interactions)

**Checkpoint**: User Stories 1-4 complete - full AI-powered insights delivered

---

## Phase 7: User Story 5 - Profile Management (Priority: P3)

**Goal**: Allow users to view and update their profile information

**Independent Test**: Access settings, update role/goal, verify changes persisted and reflected in summaries

### Tests for User Story 5

- [X] T057 [P] [US5] Unit test for profile update in tests/unit/test_profile_service.py (update fields, validation, file overwrite, timestamp update)
- [X] T058 [P] [US5] Integration test for settings flow in tests/integration/test_settings.py (open settings, edit profile, save, verify profile.json updated)

### Implementation for User Story 5

- [X] T059 [P] [US5] Create settings UI frame in ui/settings.py (CustomTkinter.CTkFrame, form fields pre-populated with existing profile, save/cancel buttons)
- [X] T060 [US5] Implement profile update logic in services/profile_service.py (load existing profile, apply changes, validate, update last_updated, save)
- [X] T061 [US5] Add settings menu item in ui/main_window.py (menu bar or button to open settings frame, switch frames)
- [X] T062 [US5] Implement profile change validation in ui/settings.py (re-use onboarding validation logic, show error messages, enable save button only when valid)

**Checkpoint**: All user stories complete - full application functional

---

## Phase 8: Enhanced Features - Work State & Streaks (Priority: P2 from clarifications)

**Goal**: Persist work state across sessions and track productive streaks

**Independent Test**: Complete session, verify work state saved, verify streak incremented

### Tests for Enhanced Features

- [ ] T063 [P] [Enh] Unit test for WorkState model in tests/unit/test_work_state.py (session_summary, completed_tasks list, streak_count, productive session logic)
- [ ] T064 [P] [Enh] Integration test for state persistence in tests/integration/test_state_persistence.py (save state, load state, streak increment, backup recovery)

### Implementation for Enhanced Features

- [ ] T065 [P] [Enh] Create WorkState model in models/work_state.py (session_summary, completed_tasks list, timestamp, streak_count, last_productive_session, focus_score, total_tracking_minutes)
- [ ] T066 [Enh] Implement state manager in services/state_manager.py (save_work_state, load_work_state, increment_streak, determine_productive_session)
- [ ] T067 [Enh] Add work state save on session end in services/tracker.py (call state_manager on stop tracking, calculate session stats, detect task accomplishments)
- [ ] T068 [Enh] Display previous session work on launch in ui/main_window.py (load work_state, show completed tasks, show streak count, notification popup)
- [ ] T069 [Enh] Implement productive session logic in services/state_manager.py (criteria: >=30 min tracking, focus_score >=50, >=1 task accomplishment)

---

## Phase 9: Enhanced Features - Single Instance Enforcement (Priority: P2 from clarifications)

**Goal**: Ensure only one app instance per user login session

**Independent Test**: Launch app twice, verify second instance activates first

### Tests for Single Instance

- [ ] T070 [P] [Enh] Unit test for instance manager in tests/unit/test_instance_manager.py (mutex creation, first instance detection, lock release, stale lock cleanup)
- [ ] T071 [Enh] Integration test for single instance in tests/integration/test_single_instance.py (launch app, second launch activates first, cleanup on exit)

### Implementation for Single Instance

- [ ] T072 [P] [Enh] Implement instance manager in services/instance_manager.py (Windows named mutex, file-based fallback, is_first_instance, activate_existing_instance)
- [ ] T073 [Enh] Add instance check on startup in src/main.py (call instance_manager, exit if not first instance, send WM_USER message to activate existing window)
- [ ] T074 [Enh] Implement existing window activation in services/instance_manager.py (find window handle, bring to foreground, restore if minimized)
- [ ] T075 [Enh] Add lock release in atexit handler in src/main.py (cleanup mutex or lock file on app exit, crash recovery)

---

## Phase 10: Enhanced Features - System Event Interception (Priority: P2 from clarifications)

**Goal**: Intercept shutdown/restart/sleep events and prompt for summary

**Independent Test**: Trigger shutdown, verify prompt appears, verify data saved before shutdown

### Tests for Event Interception

- [ ] T076 [P] [Enh] Unit test for event interceptor in tests/unit/test_event_interceptor.py (WM_QUERYENDSESSION handling, timeout enforcement, callback registration)
- [ ] T077 [Enh] Integration test for shutdown flow in tests/integration/test_shutdown_intercept.py (trigger shutdown event, show prompt, save state, allow shutdown)

### Implementation for Event Interception

- [ ] T078 [P] [Enh] Implement event interceptor in services/event_interceptor.py (WM_QUERYENDSESSION handler, register_shutdown_handler, block_shutdown, allow_shutdown)
- [ ] T079 [Enh] Create shutdown prompt dialog in ui/notifications.py (modal dialog, "Generate summary?" question, Yes/No buttons, 5-second countdown)
- [ ] T080 [Enh] Wire event interceptor to main window in ui/main_window.py (register handler, trigger prompt on WM_QUERYENDSESSION, flush all data before allowing shutdown)
- [ ] T081 [Enh] Implement auto-save before shutdown in services/tracker.py (force log flush, save work_state with current session data, ensure atomic writes complete)

---

## Phase 11: Enhanced Features - Task Celebration Notifications (Priority: P2 from clarifications)

**Goal**: Detect task accomplishments and show celebratory notifications

**Independent Test**: Trigger task detection, verify star flash notification appears

### Tests for Task Celebrations

- [ ] T082 [P] [Enh] Unit test for task accomplishment detection in tests/unit/test_ai_service.py (mock Gemini API, test pattern recognition, parse task list)
- [ ] T083 [Enh] Unit test for notification display in tests/unit/test_notifications.py (star flash widget, auto-dismiss, click handler)

### Implementation for Task Celebrations

- [ ] T084 [P] [Enh] Implement task accomplishment detection in services/ai_service.py (detect_task_accomplishments method, send logs to AI, parse task descriptions, return list)
- [ ] T085 [Enh] Create star flash notification widget in ui/notifications.py (popup window, star animation, task description, 5-second auto-dismiss, click-to-dismiss)
- [ ] T086 [Enh] Integrate task detection with tracker in services/tracker.py (periodic detection every 10 minutes, trigger notification via UI thread)
- [ ] T087 [Enh] Add tasks to work state in services/tracker.py (accumulate completed_tasks list, save to work_state.json)

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T088 [P] Add clear history functionality in ui/settings.py (button to delete logs.json, confirmation dialog, clear data directory)
- [ ] T089 [P] Implement large file warning in utils/log_handler.py (check logs.json size >50MB, warn user, suggest cleanup, continue logging)
- [ ] T090 [P] Add error recovery for corrupted files in utils/file_handler.py (detect .bak files, restore from backup, log corruption, create new file if all backups fail)
- [ ] T091 Create user guide in docs/user-guide.md (feature overview, setup instructions, usage examples, troubleshooting)
- [ ] T092 [P] Performance test 8-hour tracking run in tests/integration/test_long_running.py (simulate 8 hours of tracking, verify memory <500MB, no thread leaks, log file integrity)
- [ ] T093 Code cleanup and refactoring (remove unused imports, consistent naming, PEP 8 compliance, type hints)
- [ ] T094 [P] Add additional unit tests for edge cases in tests/unit/test_edge_cases.py (empty window titles, special characters, clock changes, inactive periods)
- [ ] T095 Security hardening (API key never in code, validate file paths, sanitize log output, no PII in logs)
- [ ] T096 Validate quickstart.md setup instructions (run through setup guide, verify all steps work, fix documentation errors)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - US1 (Onboarding) - P1 - Can start after Foundational
  - US2 (Tracking) - P1 - Can start after Foundational (parallel with US1 if team capacity)
  - US3 (Focus Score) - P2 - Depends on US2 for tracking data, can start after US2 complete
  - US4 (Summary) - P2 - Depends on US2 for tracking data, can start after US2 complete (parallel with US3)
  - US5 (Profile Management) - P3 - Depends on US1, can start after US1 complete (parallel with US2/3/4)
- **Enhanced Features (Phases 8-11)**: Depend on core user stories
  - Phase 8 (Work State) - P2 - Depends on US2 (tracking) and US4 (AI task detection)
  - Phase 9 (Single Instance) - P2 - Independent, can start after Foundational
  - Phase 10 (Event Interception) - P2 - Depends on Phase 8 (work state save)
  - Phase 11 (Task Celebration) - P2 - Depends on US4 (AI detection)
- **Polish (Phase 12)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (Onboarding)**: No dependencies on other stories - foundational
- **US2 (Tracking)**: No dependencies on other stories - foundational
- **US3 (Focus Score)**: Depends on US2 (needs tracking data) - can develop in parallel until integration
- **US4 (Daily Summary)**: Depends on US2 (needs tracking data) - can develop in parallel until integration
- **US5 (Profile Management)**: Depends on US1 (needs profile created) - can develop in parallel until integration

### Within Each User Story

- Tests MUST be written before implementation (TDD approach)
- Models before services
- Services before UI
- UI integration before validation
- Core implementation before logging
- Story complete before moving to next priority

### Parallel Opportunities

All tasks marked [P] can run in parallel:

**Setup Phase Parallel Tasks**:
- T003, T004, T005, T006, T007 (all configuration files)

**Foundational Phase Parallel Tasks**:
- T009, T010, T011, T012, T013 (utilities and base components)

**US1 Parallel Tasks**:
- Tests: T015, T016, T017 (can write all tests together)
- Models/Services: T018, T019 (model and UI can be parallel)

**US2 Parallel Tasks**:
- Tests: T025, T026, T027, T028
- Models: T029, T030

**After Foundational Phase**:
- US1 (Phase 3) and US2 (Phase 4) can proceed in parallel if team capacity allows
- US3 (Phase 5) and US4 (Phase 6) can proceed in parallel after US2 completes

**Enhanced Features**:
- Phase 9 (Single Instance) can proceed in parallel with US2/3/4/5
- Phase 10 (Event Interception) and Phase 11 (Task Celebration) can proceed in parallel after their dependencies are met

**Polish Phase**:
- T088, T089, T090, T094, T095, T096 all marked [P] and can run in parallel

---

## Parallel Example: User Story 2 (Live Activity Tracking)

```bash
# Phase 4: Launch all tests together
T025: Unit test for ActivityLog model
T026: Unit test for tracker service
T027: Unit test for browser filter
T028: Integration test for tracking flow

# After tests pass, launch all models together
T029: Create ActivityLogEntry model
T030: Create logs.json file structure handler

# Complete service and UI sequentially
T031: Implement tracker service (depends on T029, T030)
T032-T038: Remaining implementation tasks
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T014)
3. Complete Phase 3: User Story 1 - Onboarding (T015-T024)
4. Complete Phase 4: User Story 2 - Live Tracking (T025-T038)
5. **STOP and VALIDATE**: Test core MVP independently - onboarding + tracking work
6. Deploy/demo MVP if ready

### Incremental Delivery (Recommended)

1. Complete Setup + Foundational → Foundation ready
2. Add US1 (Onboarding) + US2 (Tracking) → Test independently → **Deploy/Demo MVP!**
3. Add US3 (Focus Score) + US4 (Daily Summary) → Test independently → Deploy/Demo
4. Add US5 (Profile Management) → Test independently → Deploy/Demo
5. Add Enhanced Features (Phases 8-11) → Test and Deploy
6. Polish (Phase 12) → Final Release

### Parallel Team Strategy

With 2-3 developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (Onboarding) + US5 (Profile Management)
   - Developer B: US2 (Tracking) → then US3 (Focus Score) + US4 (Daily Summary)
   - Developer C: Enhanced Features (Phases 8-11) after core stories done
3. Stories complete and integrate independently

---

## Notes

- **[P] tasks**: Different files, no dependencies, safe to parallelize
- **[Story] label**: Maps task to specific user story for traceability
- **Each user story**: Independently completable and testable
- **TDD approach**: Tests written first, verified to fail before implementation
- **Commit often**: After each task or logical group
- **Checkpoints**: Validate story independently before proceeding
- **Avoid**: Vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

**Total Tasks**: 96
- Setup: 7 tasks
- Foundational: 7 tasks
- US1 (Onboarding): 10 tasks (3 tests + 7 implementation)
- US2 (Tracking): 14 tasks (4 tests + 10 implementation)
- US3 (Focus Score): 9 tasks (2 tests + 7 implementation)
- US4 (Daily Summary): 9 tasks (2 tests + 7 implementation)
- US5 (Profile Management): 6 tasks (2 tests + 4 implementation)
- Enhanced Features: 25 tasks (6 tests + 19 implementation)
- Polish: 9 tasks

**Parallel Opportunities**: 43 tasks marked [P] can be parallelized
**MVP Scope**: 47 tasks (Setup + Foundational + US1 + US2)
**Full Scope**: 96 tasks (all phases)

**Estimated Effort**:
- MVP: ~2 weeks (Setup + Foundational + US1 + US2)
- Full Product: ~4 weeks (all user stories + enhanced features + polish)
