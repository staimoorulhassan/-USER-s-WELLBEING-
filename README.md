# User's Wellbeing - Desktop Tracking Application

A desktop application that monitors your computer activity and provides AI-powered insights into your work patterns and wellbeing.

## Features

- **Onboarding**: Set up your profile with your name, role, and main goal
- **Live Activity Tracking**: Real-time monitoring of your active windows
- **Focus Score**: AI-calculated metric to assess your productivity
- **Daily Summaries**: Intelligent summaries of your work patterns
- **Task Celebrations**: Get notified when you accomplish tasks
- **Work State Persistence**: Continue where you left off across sessions
- **Privacy-First**: All data stored locally, nothing sent to the cloud without your consent

## Prerequisites

- Python 3.11 or higher
- Windows 10/11 (pywin32 specific)
- Google AI Studio API key ([Get yours here](https://makersuite.google.com/app/apikey))

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. Configure your API key:
   - Copy `.env.example` to `.env`
   - Add your Gemini API key
5. Run the application:
   ```bash
   python src/main.py
   ```

## Usage

### First Launch

1. Complete the onboarding form with your name, role, and main goal
2. Click "Start Tracking" to begin monitoring your activity
3. View your live feed and focus score update in real-time

### Generating Summaries

1. Track your activity for some time
2. Click "Stop & Summarize" to generate an AI-powered daily summary
3. Review insights about your productivity patterns and goal alignment

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
```

## Technology Stack

- **Language**: Python 3.11+
- **UI Framework**: CustomTkinter
- **Window Tracking**: pywin32 (Windows API)
- **AI Integration**: Google Gemini API
- **Storage**: Local JSON files

## Privacy

All your data is stored locally on your computer. The only time data is sent to the cloud is when you explicitly request a daily summary.

## License

MIT License - see LICENSE file for details.
