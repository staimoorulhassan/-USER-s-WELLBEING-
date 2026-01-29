# Quickstart Guide

**Feature**: User's Wellbeing - Desktop Tracking Application
**Date**: 2025-01-27
**Audience**: Developers setting up the development environment

---

## Prerequisites

### Required Software

1. **Python 3.11+**
   ```bash
   python --version  # Should show 3.11 or higher
   ```

2. **Git**
   ```bash
   git --version
   ```

3. **Windows 10/11** (required for pywin32 window tracking)
   - For future macOS/Linux support, platform-specific window APIs needed

### Required Accounts

1. **Google AI Studio API Key** (for Gemini API)
   - Sign up at: https://makersuite.google.com/app/apikey
   - Create API key (free tier: 60 queries/minute)
   - Keep secure - never commit to git

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone <repository-url>
cd wellbeing
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux (future support)
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**If requirements.txt doesn't exist yet**:
```bash
pip install customtkinter pywin32 google-generativeai pytest pytest-qt
```

### 4. Configure API Key

Create `.env` file in project root:

```bash
# Windows (Command Prompt)
type NUL > .env

# Windows (PowerShell)
New-Item -Path . -Name ".env" -ItemType File
```

Add to `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

**Or use environment variable** (recommended for security):
```bash
# Windows (Command Prompt)
setx GEMINI_API_KEY "your_api_key_here"

# Windows (PowerShell)
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your_api_key_here', 'User')
```

### 5. Create Data Directory

```bash
# Windows
mkdir %USERPROFILE%\.wellbeing

# Or let application create on first launch
```

---

## Project Structure

```
wellbeing/
├── src/                    # Source code
│   ├── main.py            # Entry point
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   ├── ui/                # CustomTkinter UI
│   └── utils/             # Utilities
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── data/                  # Runtime data (gitignored)
│   ├── profile.json
│   ├── logs.json
│   └── work_state.json
├── docs/                  # Additional documentation
├── .env                   # API key (gitignored)
├── .gitignore
├── pyproject.toml         # Dependencies
└── README.md
```

---

## Development Workflow

### Running the Application

```bash
# From project root
python src/main.py
```

**Expected behavior**:
1. First launch: Shows onboarding screen
2. Enter profile information
3. Dashboard appears with tracking controls

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_tracker.py

# Run with verbose output
pytest -v
```

### Code Quality Checks

```bash
# Format code (if using black)
black src/ tests/

# Lint (if using pylint)
pylint src/

# Type checking (if using mypy)
mypy src/
```

---

## Development Tasks

### Phase 1: Foundation (Week 1)

**Priority: P1 (Onboarding & Tracking)**

1. **Setup project structure**
   - [ ] Create directory layout
   - [ ] Initialize git repository
   - [ ] Setup pyproject.toml with dependencies
   - [ ] Create .env.example template

2. **Implement data models**
   - [ ] User Profile model (models/profile.py)
   - [ ] Activity Log model (models/activity_log.py)
   - [ ] Work State model (models/work_state.py)
   - [ ] JSON file handlers (utils/file_handler.py)

3. **Build onboarding UI**
   - [ ] Onboarding screen (ui/onboarding.py)
   - [ ] Form validation (name, role, goal)
   - [ ] Profile save/load logic

4. **Implement tracker service**
   - [ ] Window polling engine (services/tracker.py)
   - [ ] Browser suffix filtering (utils/browser_filters.py)
   - [ ] Background thread management
   - [ ] Log file persistence

### Phase 2: Core Features (Week 2)

**Priority: P2 (Dashboard & AI Integration)**

1. **Build dashboard UI**
   - [ ] Main dashboard frame (ui/dashboard.py)
   - [ ] Focus Score display
   - [ ] Live Feed (scrollable list)
   - [ ] Start/Stop tracking buttons

2. **Integrate AI service**
   - [ ] Gemini API client (services/ai_service.py)
   - [ ] Focus Score calculation
   - [ ] Daily summary generation
   - [ ] Error handling & timeouts

3. **Add work state persistence**
   - [ ] State manager service (services/state_manager.py)
   - [ ] Session end detection
   - [ ] Work state save/load

### Phase 3: Enhanced Features (Week 3)

**Priority: P3 (Engagement & Polish)**

1. **Single instance enforcement**
   - [ ] Instance manager (services/instance_manager.py)
   - [ ] Named mutex implementation
   - [ ] Existing window activation

2. **System event interception**
   - [ ] Shutdown/sleep hook (services/event_interceptor.py)
   - [ ] Summary prompt dialog
   - [ ] Graceful data flush

3. **Task celebration system**
   - [ ] AI task accomplishment detection
   - [ ] Star flash notification (ui/notifications.py)
   - [ ] Streak tracking logic

4. **Settings & options**
   - [ ] Settings screen (ui/settings.py)
   - [ ] Notification preferences
   - [ ] Clear history functionality

### Phase 4: Testing & Polish (Week 4)

**Priority: P4 (Quality & Release)**

1. **Test coverage**
   - [ ] Unit tests for all services
   - [ ] Integration tests for flows
   - [ ] UI automation tests
   - [ ] Edge case testing

2. **Performance optimization**
   - [ ] Memory leak testing (8-hour run)
   - [ ] Large log file handling
   - [ ] UI responsiveness checks

3. **Documentation**
   - [ ] User guide (docs/user-guide.md)
   - [ ] Developer documentation
   - [ ] API documentation (if external)

4. **Packaging**
   - [ ] PyInstaller configuration
   - [ ] Create distributable .exe
   - [ ] Installer generation (optional)

---

## Testing Strategy

### Unit Tests

Test individual components in isolation:

```python
# tests/unit/test_tracker.py
def test_browser_suffix_filtering():
    from utils.browser_filters import filter_window_title
    assert filter_window_title("GitHub - Google Chrome") == "GitHub"
    assert filter_window_title("Stack Overflow - Mozilla Firefox") == "Stack Overflow"
```

### Integration Tests

Test component interactions:

```python
# tests/integration/test_tracking_flow.py
def test_onboarding_to_tracking_flow(tmp_path):
    # 1. Launch app (detects no profile, shows onboarding)
    # 2. Fill onboarding form
    # 3. Verify profile.json created
    # 4. Verify dashboard shown
    # 5. Click "Start Tracking"
    # 6. Simulate window switches
    # 7. Verify logs.json updated
    pass
```

### Mock AI Service

Avoid API calls during tests:

```python
# tests/unit/test_ai_service.py
@patch('services.ai_service.GenerativeModel')
def test_focus_score_calculation(mock_gemini):
    mock_response = Mock()
    mock_response.text = "75"
    mock_gemini.return_value.generate_content.return_value = mock_response

    from services.ai_service import calculate_focus_score
    score = calculate_focus_score(mock_logs)
    assert score == 75
```

---

## Debugging Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect Window Titles

```python
import win32gui
hwnd = win32gui.GetForegroundWindow()
title = win32gui.GetWindowText(hwnd)
print(f"Active window: {title}")
```

### Monitor Memory Usage

```bash
# Track memory leaks during long-running sessions
# Use Windows Task Manager or Process Explorer
# Look for:
# - Handle count (should stabilize)
# - Memory usage (should not grow indefinitely)
# - Thread count (should be 2-3 threads)
```

### Common Issues

**Issue**: `ImportError: No module named 'win32gui'`
- **Solution**: Install pywin32: `pip install pywin32`

**Issue**: Application won't start (flashes and closes)
- **Solution**: Run from command line to see error: `python src/main.py`

**Issue**: "API key not found"
- **Solution**: Check .env file exists and contains GEMINI_API_KEY

**Issue**: Background thread not stopping
- **Solution**: Ensure threading.Event is set and thread joined with timeout

---

## Build & Distribution

### Create Executable with PyInstaller

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=assets/icon.ico src/main.py
```

Output: `dist/main.exe` (single executable, no Python required)

### Distribution Options

1. **Direct download**: Host .exe on GitHub Releases
2. **Installer**: Use Inno Setup for Windows installer
3. **Microsoft Store**: Requires packaging and certification (future)

---

## Contributing Guidelines

### Code Style

- Follow PEP 8 (Python style guide)
- Use 4 spaces for indentation
- Max line length: 100 characters
- Use descriptive variable names (avoid abbreviations)

### Git Commit Messages

```
feat: Add window tracking service
fix: Handle empty window titles gracefully
docs: Update README with setup instructions
test: Add integration test for onboarding flow
```

### Pull Request Process

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit
3. Run tests: `pytest`
4. Push to remote: `git push origin feature/your-feature`
5. Create pull request on GitHub
6. Request review and address feedback

---

## Resources

### Documentation

- [CustomTkinter Documentation](https://customtkinter.tomschimansky.com/)
- [pywin32 Documentation](https://github.com/mhammond/pywin32)
- [Google Gemini API](https://ai.google.dev/docs)
- [Python Threading](https://docs.python.org/3/library/threading.html)

### Community

- Stack Overflow: Tag questions with `python` `pywin32` `customtkinter`
- GitHub Issues: Report bugs and feature requests

---

## Troubleshooting

### Application crashes on startup

**Symptoms**: Application window appears briefly then closes

**Diagnosis**:
```bash
python src/main.py
# Look for traceback in console output
```

**Common causes**:
- Missing dependencies (pip install missing package)
- Corrupted profile.json (delete and re-run onboarding)
- Missing data directory (create manually)

### Tracking not working

**Symptoms**: Live feed not updating despite window switches

**Diagnosis**:
```python
# Add debug logging in tracker.py
logging.debug(f"Active window: {window_title}")
```

**Common causes**:
- Background thread crashed (check logs)
- Window title is empty (handle gracefully)
- File write permission issue (check data directory permissions)

### AI service timeouts

**Symptoms**: Summary generation hangs or shows timeout error

**Diagnosis**:
```bash
# Test API key manually
curl -H "Content-Type: application/json" \
  -H "x-goog-api-key: YOUR_API_KEY" \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}' \
  https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent
```

**Common causes**:
- Invalid API key (regenerate in Google AI Studio)
- Network connectivity issue (check internet connection)
- Rate limiting exceeded (wait 60 seconds)
- Timeout too short (increase in constants.py)

---

## Next Steps

1. **Read the spec**: [spec.md](./spec.md) for detailed requirements
2. **Review research**: [research.md](./research.md) for technical decisions
3. **Study data model**: [data-model.md](./data-model.md) for entity definitions
4. **Start coding**: Begin with Phase 1 tasks above

**Happy tracking! 🎯**
