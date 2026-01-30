# Wellbeing Desktop Tracker 🧠✨

A **privacy-first, AI-powered desktop companion** that helps you understand your work habits, track productivity, and maintain wellbeing. Built from scratch with a focus on performance, observability, and flexibility.

![Status](https://img.shields.io/badge/Status-Active-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Observability](https://img.shields.io/badge/Observability-Opik-orange)

## 🚀 Key Features

* **🤖 Multi-Provider AI Intelligence**:
  * Generates deep daily summaries and productivity insights.
  * **Flexible Backend**: Seamlessly switch between **Pollinations.ai** (Free/OpenAI-compatible), **Google Gemini**, and **Z.ai**.
  * **Smart Optimizations**: Includes "Triviality Filtering" to bypass AI calls for short sessions (<10m), saving cost and time.
* **📊 Real-Time Focus Tracking**: Automatically monitors active windows and applications to calculate a live "Focus Score" aligned with your personal goals.
* **🔍 Enterprise-Grade Observability**: Integrated **Opik** tracing provides granular visibility into AI prompts, latencies, and output quality.
* **⚡ Performance First**:
  * **Async UI**: Heavy AI tasks run in background threads, keeping the interface snappy.
  * **Local Processing**: Logs are pre-processed and aggregated locally to minimize data sent to APIs.
* **🔒 Privacy-Centric**: All raw activity data stays on your machine (`data/logs.json`). Cloud APIs are only contacted for explicit summary generation.

## 🛠️ Technology Stack

* **Core**: Python 3.11+
* **GUI**: CustomTkinter (Modern, Dark-Mode ready)
* **OS Integration**: `pywin32` for low-level window tracking
* **AI Integration**: `google-genai`, `openai` SDK (compatible with Pollinations/Z.ai)
* **Monitoring**: `opik` SDK for distributed tracing

## 📦 Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yourusername/wellbeing-tracker.git
    cd wellbeing-tracker
    ```

2. **Create Virtual Environment**

    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3. **Install Dependencies**

    ```bash
    pip install . # Installs the package in editable mode
    ```

4. **Configuration (.env)**
    Create a `.env` file in the root directory:

    ```ini
    # Select Provider: "pollinations", "gemini", or "zai"
    AI_PROVIDER=pollinations
    
    # API Keys (Set the one matching your provider)
    POLLINATIONS_API_KEY=your_key_here
    GEMINI_API_KEY=your_key_here
    
    # Optional: Observability
    OPIK_API_KEY=your_opik_key
    ```

## 🚀 Usage

1. **Run the App**:

    ```bash
    .\run.bat
    ```

2. **Onboarding**: Enter your Name, Role (e.g., "Developer"), and Main Goal.
3. **Track**: The app runs in the background. Minimize it and work.
4. **Summarize**: Click **"Stop & Summarize"**.
    * If activity > 10 mins: You get a detailed AI walkthrough of your day.
    * If activity < 10 mins: Instant feedback (saving AI quota).

## 📈 Observability (Opik)

This project uses **Opik** to track AI reliability. Traces include:

* **Child Spans**: Explicitly tracks the `check_activity_significance` step.
* **Metadata**: Logs token usage, latency, and provider details.
* **Tags**: Automatically tags traces with `optimization_triviality_check` for easy filtering.

## 📄 License

MIT License. Free to use and modify.
