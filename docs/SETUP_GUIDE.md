# Setup Guide for Wellbeing Desktop Tracker

This guide provides detailed instructions for setting up and configuring the Wellbeing Desktop Tracker application.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [API Key Setup](#api-key-setup)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)
8. [Development Setup](#development-setup)

## Prerequisites

### System Requirements
- **Operating System**: Windows 10 or Windows 11
- **Python**: 3.11 or higher (64-bit version recommended)
- **Memory**: At least 512MB RAM
- **Storage**: 100MB free disk space
- **Network**: Internet connection (for AI features)

### Required Software
1. **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Verify installation: `python --version`
2. **Git** (optional) - [Download Git](https://git-scm.com/download/win)

## Installation Steps

### Method 1: Using Git (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Taimoor/wellbeing-desktop-tracker.git
   cd wellbeing-desktop-tracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

### Method 2: Manual Download

1. **Download the repository**
   - Visit: https://github.com/Taimoor/wellbeing-desktop-tracker
   - Click "Code" → "Download ZIP"
   - Extract the ZIP file to your desired location

2. **Open Command Prompt** in the extracted folder

3. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -e .
   ```

## Configuration

### Environment Setup

1. **Create environment file**
   ```bash
   copy .env.example .env
   ```

2. **Edit the .env file**
   Open `.env` file with a text editor (like VS Code, Notepad++, or Notepad)

   ```env
   # Google Gemini API Key (required)
   # Get your free key from: https://makersuite.google.com/app/apikey
   GEMINI_API_KEY=your-gemini-api-key-here

   # Opik API Key (optional - for performance tracking)
   # Get your key from: https://www.comet.com/opik
   OPIK_API_KEY=your-opik-api-key-here

   # Application settings (optional - customize as needed)
   WELLBEING_DATA_DIR=~/.wellbeing
   POLLING_INTERVAL_SECONDS=5
   TRACKING_TIMEOUT_SECONDS=30
   SHUTDOWN_TIMEOUT_SECONDS=5
   ```

### API Key Setup

#### Gemini API Key (Required)

1. **Get your API key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the generated key

2. **Add to .env file**:
   ```bash
   # Replace "your-gemini-api-key-here" with your actual key
   GEMINI_API_KEY=AIzaSyYourActualApiKeyHere
   ```

#### Opik API Key (Optional)

For performance monitoring and debugging:

1. **Sign up for Opik**:
   - Visit [Opik](https://www.comet.com/opik)
   - Create your account

2. **Get your API key**:
   - Go to your dashboard
   - Find your API key in settings

3. **Add to .env file** (optional):
   ```bash
   OPIK_API_KEY=your-opik-api-key-here
   ```

## Running the Application

### First Launch

1. **Activate virtual environment** (if not already active):
   ```bash
   venv\Scripts\activate
   ```

2. **Start the application**:
   ```bash
   python src/main.py
   ```

3. **Complete onboarding**:
   - Fill in your name
   - Enter your role/profession
   - Set your main goal
   - Click "Create Profile"

### Daily Use

1. **Start Tracking**: Click the green "Start Tracking" button
2. **Work normally**: The app runs in the background
3. **View insights**: Monitor your focus score and live feed
4. **Generate summaries**: Click "Stop & Summarize" when done

## Troubleshooting

### Common Issues

**Application won't start**

- **Error**: `'python' is not recognized as an internal or external command`
  - **Solution**: Ensure Python is installed and added to PATH
  - **Check**: `python --version`

- **Error**: `ModuleNotFoundError: No module named 'customtkinter'`
  - **Solution**: Activate virtual environment and reinstall dependencies
  - **Commands**:
    ```bash
    venv\Scripts\activate
    pip install -e .
    ```

- **Error**: `'venv' is not recognized...`
  - **Solution**: Ensure you're in the correct directory
  - **Check**: You should see `wellbeing-desktop-tracker` folder

**API Key Issues**

- **Error**: `API key not set` or `GEMINI_API_KEY environment variable not set`
  - **Solution**:
    1. Check `.env` file exists in root directory
    2. Verify `GEMINI_API_KEY` is correctly spelled
    3. Restart the application after changes

- **Error**: `Failed to initialize Gemini API: Invalid API key`
  - **Solution**:
    1. Verify your API key is correct
    2. Check for extra spaces or characters
    3. Get a new key from Google AI Studio

**Window Tracking Issues**

- **No window titles appearing**:
  - Run as administrator: Right-click Command Prompt → "Run as administrator"
  - Check if other monitoring software is running
  - Ensure you're on Windows 10/11

**Focus Score Not Updating**

- **Score stuck at "N/A"**:
  - Ensure you've tracked for at least 30 minutes
  - Check internet connection for AI processing
  - Verify your activity log has entries

**UI Issues**

- **Window too large/small**:
  - Application is now optimized for 650x480
  - If scaling issues occur, adjust display scaling in Windows settings

### Error Messages and Solutions

| Error Message | Solution |
|---------------|----------|
| `ImportError: No module named 'pywin32'` | `pip install pywin32` |
| `ValueError: transparency is not allowed` | Update to latest CustomTkinter version |
| `ConnectionError: Failed to connect to Gemini` | Check internet connection |
| `PermissionError: [Errno 13] Permission denied` | Run as administrator |

### Getting Help

1. **Check the console** for error messages
2. **Review this setup guide**
3. **Search existing issues**: [GitHub Issues](https://github.com/Taimoor/wellbeing-desktop-tracker/issues)
4. **Create a new issue** with:
   - Your operating system
   - Python version (`python --version`)
   - Error message (copy and paste)
   - Steps to reproduce the issue

## FAQ

### General Questions

**Q: Is this application free?**
A: Yes! The application is free to use. The Gemini API has a free tier that's sufficient for daily use.

**Q: Is my data secure?**
A: Yes! All data is stored locally on your computer. Only summaries are sent to Google Gemini with your permission.

**Q: Can I use this on Mac/Linux?**
A: Currently, the application is Windows-only due to pywin32 dependency. Mac/Linux support may be added in future versions.

**Q: How much data does it use?**
A: Minimal. Only small JSON files are stored locally. AI processing uses ~1-2MB per request.

### Technical Questions

**Q: Why Python 3.11+?**
A: The application uses modern Python features and benefits from performance improvements in Python 3.11+.

**Q: Can I run this without the virtual environment?**
A: Not recommended. Virtual environments prevent dependency conflicts and keep your system clean.

**Q: How do I update the application?**
A: Simply pull the latest changes and reinstall:
```bash
git pull
pip install -e .
```

**Q: Can I customize the UI?**
A: The UI is designed to be clean and functional. Limited customization options may be added in future versions.

### Privacy Questions

**Q: Is my activity data sent anywhere?**
A: No. Activity data is stored locally. Only when you explicitly request a summary is data sent to Google Gemini.

**Q: Can I work offline?**
A: Yes! Tracking works offline. AI summaries require internet access.

**Q: Where are my data files stored?**
A: By default: `C:\Users\<YourUsername>\.wellbeing\`

## Development Setup

### For Contributors

If you want to contribute to the project:

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/wellbeing-desktop-tracker.git
   cd wellbeing-desktop-tracker
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests**:
   ```bash
   pytest
   ```

5. **Format code**:
   ```bash
   black src/ tests/
   ```

### Code Style Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Write comprehensive docstrings
- Include tests for new features

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_tracker.py

# Run with verbose output
pytest -v
```

---

Need more help? Check the [main README](../README.md) or open an [issue](https://github.com/Taimoor/wellbeing-desktop-tracker/issues).