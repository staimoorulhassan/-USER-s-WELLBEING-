# 🚀 Quick Start Guide

## 1. Setup (One-time)

```bash
# Virtual environment already created
# Dependencies already installed

# Configure your API key
# Edit .env file and add:
GEMINI_API_KEY=AIzaSyAmPQXzpHt8Rq82FetKP3AuXyq3LfCITGU
```

## 2. Run the Application

```bash
# Option 1: Double-click
run.bat

# Option 2: Command line
venv\Scripts\activate
python src\main.py
```

## 3. First Time Use

1. **Onboarding**: Enter your name, role, and main goal
2. **Dashboard**: Click "Start Tracking" to begin
3. **Live Feed**: Watch your window activity update in real-time
4. **Stop Tracking**: Click "Stop Tracking" when done

## 4. Your Data

All data stored in `C:\Users\Taimoor\.wellbeing\`:
- `profile.json` - Your profile
- `logs.json` - Activity logs
- `logs/wellbeing.log` - Application logs

## ✅ MVP Features Working

- ✅ User onboarding with validation
- ✅ Profile persistence
- ✅ Background window tracking (5s polling)
- ✅ Browser suffix filtering
- ✅ Live activity feed
- ✅ Start/Stop tracking controls
- ✅ Automatic logging
- ✅ AI-powered focus scores
- ✅ Daily summaries with recommendations
- ✅ Settings menu (File > Settings) to update profile

## 🔮 Coming Soon (Next Phases)

- ⏳ Work State Persistence (streaks, session tracking)
- ⏳ Single Instance Enforcement
- ⏳ Shutdown Interception
- ⏳ Task Celebrations (AI-detected accomplishments)

## 🐛 Troubleshooting

**Issue**: ModuleNotFoundError
**Fix**: Make sure you're running from the project root directory

**Issue**: pywin32 errors
**Fix**: Ensure you're on Windows 10/11

**Issue**: API key errors
**Fix**: Add your GEMINI_API_KEY to .env file (not needed for MVP tracking)

---

**Ready to track! 🎯**
