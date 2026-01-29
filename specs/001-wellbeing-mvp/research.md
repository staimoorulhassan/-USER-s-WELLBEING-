# Research & Technical Decisions

**Feature**: User's Wellbeing - Desktop Tracking Application
**Date**: 2025-01-27
**Status**: Complete

## Overview

This document captures research findings and technical decisions for the wellbeing tracking desktop application. All NEEDS CLARIFICATION items from the Technical Context have been resolved through research and best practices analysis.

---

## 1. Window Tracking Implementation

### Decision: Use pywin32 with polling mechanism

**Rationale**:
- **Platform-native integration**: pywin32 provides direct access to Windows API via `GetForegroundWindow()` and `GetWindowText()`, ensuring reliable window title capture
- **Simplicity**: Polling every 5 seconds is straightforward to implement, debug, and test
- **Low overhead**: 5-second interval minimizes CPU usage while providing sufficient granularity for wellbeing tracking
- **No event hooking complexity**: Avoids Windows hooks (SetWinEventHook) which require COM initialization and complex cleanup

**Alternatives Considered**:
- **Event-driven hooks**: More complex, requires careful thread management, potential for system-wide instability if misconfigured
- **Cross-platform libraries (e.g., pygetwindow)**: Adds abstraction layer, less reliable on Windows, pywin32 is mature and widely-used

**Implementation Details**:
```
- Use win32gui.GetForegroundWindow() to get active window handle
- Use win32gui.GetWindowText(hwnd) to retrieve window title
- Filter browser suffixes using configurable regex patterns
- Run in separate threading.Thread with daemon=True for clean shutdown
```

**Risks & Mitigations**:
- **Risk**: Polling may miss rapid window switches (<5s duration)
- **Mitigation**: Acceptable for wellbeing use case; focusing on patterns, not instant transitions
- **Risk**: Window titles may be empty or contain special characters
- **Mitigation**: Sanitize with unicode normalization, handle empty titles gracefully

---

## 2. Single Instance Enforcement

### Decision: Use named mutex (Windows) with filesystem fallback

**Rationale**:
- **Platform-specific optimization**: Windows mutex (`CreateMutex`) provides OS-level singleton guarantee
- **Cross-session isolation**: Per-user mutex naming prevents conflicts between user accounts
- **Activation of existing instance**: SendMessage or WM_COPYDATA to bring existing window to foreground
- **Graceful degradation**: File-based lock (e.g., `.lock` file) as fallback if mutex creation fails

**Alternatives Considered**:
- **Port-based binding**: Overkill for desktop app, requires network stack
- **PID file checking**: Prone to stale PIDs if process crashes violently
- **Single-instance library (e.g., PyQtSingleApplication)**: Adds dependency, framework-specific

**Implementation Details**:
```
Mutex name: f"Global\\WellbeingApp_{getpass.getuser()}"
Fallback: ~/.wellbeing/app.lock with flock()
On second launch: Send WM_USER + 1 to existing window to activate
```

**Best Practice**:
- Clean up mutex in atexit handler for crash recovery
- Include timestamp in lock file to detect stale locks (>30 min old)

---

## 3. System Event Interception (Shutdown/Sleep)

### Decision: Use WM_QUERYENDSESSION message handler

**Rationale**:
- **Windows message loop integration**: CustomTkinter (Tkinter) runs a message pump that can intercept WM_QUERYENDSESSION
- **User prompt opportunity**: Windows allows blocking shutdown for up to 5 seconds (Registry: HKCU\Control Panel\Desktop\WaitToKillAppTimeout)
- **Graceful data flush**: Ensures logs.json and work_state.json are atomically written before system power-off

**Alternatives Considered**:
- **Shutdown block API**: More complex, requires COM, overkill for simple prompt
- **Background service with SCM**: Excessive architecture for single-user app
- **No interception**: Accept data loss risk (violates spec requirement FR-028)

**Implementation Details**:
```
Tkinter protocol handler: root.protocol("WM_DELETE_WINDOW", on_closing)
Windows-specific: win32gui.SetWindowsHookEx for WM_QUERYENDSESSION
Timeout: 5-second countdown dialog (non-cancellable after timeout)
Auto-save: Always flush data on intercept, regardless of user choice
```

**Limitations**:
- **Fast shutdown**: Force shutdown (power button hold) cannot be intercepted
- **Mitigation**: Implement periodic auto-save every 5 minutes to minimize data loss

---

## 4. AI Integration Architecture

### Decision: Synchronous API calls with adaptive timeouts

**Rationale**:
- **Simplicity**: Blocking calls in background threads avoid complex async/await patterns in UI code
- **Adaptive timeout strategy**: 5-second timeout for shutdown events (non-blocking), 30-second timeout for manual requests (user expects wait)
- **Graceful degradation**: Catch timeouts/API errors, show cached summary or friendly error message
- **Privacy compliance**: Only send data on explicit user action ("Stop & Summarize")

**Alternatives Considered**:
- **Async/await with aiohttp**: More complex, requires restructuring UI for event loop integration
- **Queue-based batching**: Over-engineered for single-user desktop app, adds persistent queue storage requirement
- **Local AI model (e.g., Ollama)**: Offline-capable but requires model download, larger resource footprint, less accurate insights

**Implementation Details**:
```
Service: google.generativeai.GenerativeModel('gemini-pro')
Timeouts: requests.post(..., timeout=5 or timeout=30)
Retry: Single retry on timeout with exponential backoff (1s, 2s)
Error handling: Specific messages for 429 (rate limit), 500 (server error), timeout
Prompt engineering: Include user goals, role, activity patterns in context window
```

**Data Privacy**:
- API key stored in environment variable (GEMINI_API_KEY) or Windows Credential Manager
- No window titles sent to AI without explicit user action
- Local logs.json never transmitted in bulk; anonymized patterns extracted server-side

---

## 5. Data Storage Strategy

### Decision: JSON files with atomic write pattern

**Rationale**:
- **Simplicity**: JSON is human-readable, easy to debug, no database setup required
- **Portability**: Users can easily backup/migrate profile.json, logs.json, work_state.json
- **Atomic writes**: Use tempfile + os.replace() pattern to prevent corruption on crash/power-loss
- **Scalability**: For single-user app with 5-second polling, JSON performance is acceptable (estimated <10k entries/day = ~5MB/month)

**Alternatives Considered**:
- **SQLite**: Adds dependency, overkill for append-only logs, harder to inspect/export
- **CSV**: Lacks structure for nested entities (profile, work_state)
- **Binary format (pickle)**: Not human-readable, security risk (code execution on load)

**Implementation Details**:
```
Atomic write pattern:
  1. Write to temporary file (tempfile.NamedTemporaryFile(mode='w', delete=False))
  2. Flush and fsync() to ensure data written to disk
  3. os.replace(temp_path, target_path) - atomic on Linux/Windows
File locking: Use portalocker or fcntl for concurrent write protection
Backup: Retain .bak files (last 3 versions) for recovery
Rotation: When logs.json > 100MB, prompt user to archive/delete
```

**Schema Definitions**:
See [data-model.md](./data-model.md) for JSON structure definitions.

---

## 6. UI Framework Selection

### Decision: CustomTkinter (wrapper around Tkinter)

**Rationale**:
- **Modern look**: CustomTkinter provides modern, rounded UI components (vs. dated Tkinter defaults)
- **Native Windows feel**: Uses Windows theming API for consistent appearance
- **Simplicity**: Declarative UI construction, event-driven programming model familiar to Python developers
- **Low learning curve**: Tkinter is built into Python, extensive documentation and community support

**Alternatives Considered**:
- **PyQt6/PySide6**: More powerful, but larger binary size (50MB+), more complex licensing (LGPLv3)
- **Electron + JavaScript**: Excessive resource footprint (Chromium + Node.js = >200MB), violates Python requirement
- **Kivy**: Cross-platform but non-native appearance, steeper learning curve

**UI Structure**:
```
MainWindow (CustomTkinter.CTkToplevel)
├── OnboardingFrame (first launch only)
├── DashboardFrame (primary view)
│   ├── Header: User name, tracking status indicator
│   ├── Focus Score: Large numeric display, trend indicator
│   ├── Live Feed: Scrollable list of recent window titles
│   └── Controls: Start/Stop Tracking buttons, Stop & Summarize
├── SettingsFrame
│   ├── Profile editor
│   ├── Notification preferences
│   └── Clear History button
└── NotificationManager: Toast/popups for task celebrations
```

**Best Practices**:
- **Threading**: Never update UI from background threads; use root.after() or queue.Queue for thread-safe UI updates
- **Responsiveness**: Keep polling thread separate from UI thread, use locks for shared state
- **Accessibility**: Use high-contrast colors, ensure keyboard navigation works

---

## 7. Background Thread Management

### Decision: Threading.Thread with daemon mode and graceful shutdown

**Rationale**:
- **Simplicity**: Python threading module is built-in, easy to use
- **Daemon mode**: Threads marked daemon=True terminate automatically when main thread exits (prevents orphaned processes)
- **Graceful shutdown**: Use threading.Event() for clean thread termination on application close
- **State isolation**: Each thread owns its state; shared access protected by locks

**Alternatives Considered**:
- **Multiprocessing**: Overkill, adds IPC complexity, higher memory overhead
- **Asyncio with run_in_executor**: More complex, requires restructuring entire app for async/await
- **Timer-based callbacks**: Tkinter's .after() is single-threaded, blocks UI during polling

**Implementation Details**:
```
Tracker thread:
  - daemon=True for auto-cleanup
  - Event() for stop_signal (checked every iteration)
  - Lock() for shared state (logs list, tracking_active flag)
  - Queue() for UI updates (thread-safe communication)

Shutdown sequence:
  1. Set stop_signal event
  2. Join thread with timeout (max 2 seconds)
  3. If timeout, mark as daemon and let OS clean up (safe for tracker thread)
```

**Risk Mitigation**:
- **Memory leaks**: Ensure circular references broken, use weakref for callbacks
- **Deadlocks**: Never acquire multiple locks simultaneously; use timeout on lock acquisition
- **Zombie threads**: Always join threads in atexit handler with timeout

---

## 8. Testing Strategy

### Decision: pytest with mocking for external dependencies

**Rationale**:
- **Industry standard**: pytest is de facto Python testing framework, rich plugin ecosystem
- **AI service mocking**: Use unittest.mock.patch to simulate Gemini API responses, avoid rate limits/costs during testing
- **UI testing**: pytest-qt provides Qt-like fixtures for CustomTkinter (simulates user interactions)
- **Fixtures**: Reusable test data in tests/fixtures/ for reproducible tests

**Test Coverage Goals**:
- Unit tests: 80%+ coverage for services (tracker, ai_service, state_manager)
- Integration tests: End-to-end flows (onboarding → tracking → summary)
- Edge cases: File corruption, network timeouts, empty window titles

**Implementation Details**:
```
Unit test example:
  @patch('services.ai_service.GenerativeModel')
  def test_focus_score_calculation(mock_gemini):
      mock_gemini.return_value.generate_content.return_value.text = "75"
      score = ai_service.calculate_focus_score(mock_logs)
      assert score == 75

Integration test example:
  def test_onboarding_to_dashboard(tmp_path):
      # Run app with temp directory
      # Simulate user input
      # Assert profile.json created and dashboard shown
```

---

## 9. Error Handling & Observability

### Decision: Structured logging + user-friendly error messages

**Rationale**:
- **Debugging**: Structured logs (JSON format) enable grep-able troubleshooting
- **User experience**: Technical errors translated to actionable messages (e.g., "Unable to connect to AI service. Check your internet connection.")
- **Crash recovery**: Log unhandled exceptions with traceback for post-mortem analysis
- **Privacy**: Never log window titles (PII), only metadata (timestamp, filtered app name)

**Implementation Details**:
```
Logging configuration:
  - Level: INFO (production), DEBUG (development)
  - Format: %(asctime)s - %(name)s - %(levelname)s - %(message)s
  - Handlers: RotatingFileHandler (max 10MB, 3 backups)
  - Path: ~/.wellbeing/app.log (user home directory)

Error categories:
  - Recoverable: Log warning, show user notification, continue operation
  - Unrecoverable: Log error, show user dialog, exit gracefully
  - Critical: Log critical, attempt data flush, exit with code 1
```

---

## 10. Dependencies & Packaging

### Decision: pyproject.toml with setuptools + PyInstaller for executable

**Rationale**:
- **Modern Python packaging**: pyproject.toml is PEP 518 standard, declarative dependencies
- **Isolated environment**: Virtual environment (venv) prevents dependency conflicts
- **Executable distribution**: PyInstaller bundles Python interpreter + dependencies into single .exe

**Core Dependencies**:
```
customtkinter>=5.2.0
pywin32>=306; sys_platform == 'win32'
google-generativeai>=0.3.0
pytest>=7.4.0
pytest-qt>=4.2.0
```

**Distribution Strategy**:
- Development: Source distribution (git clone + pip install)
- End-user: Single .exe executable via PyInstaller (--onefile mode)
- Updates: Check for updates on launch (optional feature), prompt to download new version

---

## Summary

All technical unknowns from the Technical Context section have been resolved through research and best practices analysis. The chosen technologies and patterns prioritize simplicity, reliability, and user privacy while meeting all functional requirements.

**Key Decisions**:
1. pywin32 for Windows API integration
2. Named mutex for single-instance enforcement
3. WM_QUERYENDSESSION for shutdown interception
4. Synchronous AI calls with adaptive timeouts
5. JSON files with atomic write pattern
6. CustomTkinter for modern UI
7. Threading for background operations
8. pytest with comprehensive mocking

**Next Phase**: Proceed to Phase 1 (Design Artifacts) - create data-model.md, quickstart.md, and API contracts.
