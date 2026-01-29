# Feature Specification: User's Wellbeing - Desktop Tracking Application

**Feature Branch**: `001-wellbeing-mvp`
**Created**: 2025-01-27
**Status**: Draft
**Input**: User description: "Desktop app for tracking user wellbeing with onboarding, dashboard, window activity tracking, and AI-powered daily summaries"

## Clarifications

### Session 2025-01-27

- Q: How should the Focus Score be calculated? → A: AI-generated (send activity patterns to AI for calculation)
- Q: What is the data retention policy for tracked window logs? → A: Manual cleanup (users must explicitly delete old logs)
- Q: How should the application handle multiple launch attempts? → A: Single instance only - run in background per user login session
- Q: How should the system detect task accomplishments? → A: AI-detected (AI analyzes patterns and identifies task completions)
- Q: What is the timeout behavior for AI service requests? → A: Adaptive timeout (5s for shutdown events, 30s for manual requests)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - First-Time User Onboarding (Priority: P1)

As a new user, I want to set up my profile so that the application can personalize my wellbeing tracking experience.

**Why this priority**: Without onboarding, the application cannot function - user profile data is required for all features including tracking, analysis, and personalized reports.

**Independent Test**: Can be fully tested by launching the application, entering profile information, and verifying that profile.json is created with the correct data. Delivers value by enabling the user to proceed to tracking features.

**Acceptance Scenarios**:

1. **Given** the application is launched for the first time, **When** the user enters their name, role, and main goal, **Then** the profile is saved to profile.json and the dashboard is displayed
2. **Given** a user has completed onboarding, **When** they relaunch the application, **Then** they are taken directly to the dashboard (onboarding is skipped)
3. **Given** the onboarding form is displayed, **When** the user leaves required fields empty, **Then** appropriate validation messages are shown
4. **Given** a profile.json already exists, **When** the user launches the application, **Then** existing profile data is loaded and the user can proceed to tracking

---

### User Story 2 - Live Activity Tracking (Priority: P1)

As a user, I want to see my computer activity being tracked in real-time so that I can understand my current focus and work patterns.

**Why this priority**: This is the core value proposition - users need immediate visibility into their activity to feel the application is working and to build trust in the tracking system.

**Independent Test**: Can be fully tested by starting the tracker, switching between different windows, and verifying that the live feed updates accurately. Delivers value by providing real-time transparency into user activity.

**Acceptance Scenarios**:

1. **Given** the user has completed onboarding, **When** they click "Start Tracking", **Then** a background thread begins polling the active window every 5 seconds
2. **Given** tracking is active, **When** the user switches to a different window, **Then** the new window title appears in the Live Feed within 10 seconds
3. **Given** tracking is active, **When** the active window is a browser (e.g., "Google Chrome"), **Then** browser suffixes like " - Google Chrome" are filtered out in the Live Feed
4. **Given** tracking is active, **When** the user clicks "Stop Tracking", **Then** polling stops and no new entries are added to the Live Feed
5. **Given** the application is tracking, **When** the user minimizes or closes the application window, **Then** tracking continues in the background

---

### User Story 3 - Focus Score Dashboard (Priority: P2)

As a user, I want to see a "Focus Score" metric so that I can quickly assess my productivity at a glance.

**Why this priority**: The Focus Score provides immediate value and motivation, but it depends on having tracking data first. Users can still benefit from live tracking without this score, but it enhances the overall experience.

**Independent Test**: Can be fully tested by tracking activity for a period and verifying that the Focus Score updates based on tracked windows. Delivers value by providing a quantified measure of focus.

**Acceptance Scenarios**:

1. **Given** tracking has been active for at least 5 minutes, **When** the user views the dashboard, **Then** a Focus Score is displayed (calculated from tracked activity)
2. **Given** tracking is active, **When** the user switches between productive and non-productive windows, **Then** the Focus Score updates to reflect the change
3. **Given** no tracking data exists, **When** the dashboard is displayed, **Then** the Focus Score shows a default/initial state (e.g., "N/A" or 0)

---

### User Story 4 - AI-Powered Daily Summary (Priority: P2)

As a user, I want to generate an intelligent summary of my day's activity so that I can gain insights into my work patterns and wellbeing without manually analyzing logs.

**Why this priority**: This provides high-value insights but is not required for basic tracking functionality. Users can track and view live activity without this feature, but the summary delivers the "wellbeing analysis" value proposition.

**Independent Test**: Can be fully tested by tracking activity for a period, clicking "Stop & Summarize", and verifying that a text-based summary is generated and displayed. Delivers value by transforming raw data into actionable insights.

**Acceptance Scenarios**:

1. **Given** the user has tracked activity for a period, **When** they click "Stop & Summarize", **Then** the application sends batched logs to the AI service and displays a generated summary
2. **Given** the user clicks "Stop & Summarize", **When** the AI service is unavailable or returns an error, **Then** the user sees a friendly error message and local logs are preserved
3. **Given** a summary has been generated, **When** the user views it, **Then** the summary includes insights about productivity patterns, time distribution, and alignment with stated goals
4. **Given** the user has no tracked logs, **When** they click "Stop & Summarize", **Then** an appropriate message is displayed indicating no data is available to summarize

---

### User Story 5 - Profile Management (Priority: P3)

As a user, I want to view and update my profile information so that my wellbeing tracking reflects my current goals and role.

**Why this priority**: Users can effectively use the application with their initial profile indefinitely. This enhancement allows for profile updates but is not critical for MVP functionality.

**Independent Test**: Can be fully tested by accessing profile settings, updating information, and verifying changes are persisted. Delivers value by allowing users to keep their tracking aligned with evolving goals.

**Acceptance Scenarios**:

1. **Given** the user has completed onboarding, **When** they access profile settings, **Then** they can view their current name, role, and main goal
2. **Given** the profile settings are displayed, **When** the user updates their role or goal, **Then** changes are saved to profile.json
3. **Given** the user has updated their profile, **When** they generate a new summary, **Then** the analysis reflects their updated goals and role

---

### Edge Cases

- What happens when the computer goes to sleep or hibernates while tracking is active? System intercepts sleep event and prompts for summary.
- What happens when the AI service (Gemini API) is rate-limited or returns a 429 error?
- What happens when the user's internet connection is lost during "Stop & Summarize"?
- What happens when profile.json becomes corrupted or contains invalid data?
- What happens when logs.json exceeds a large file size (e.g., >100MB)? System continues logging and warns user to manually clean up old logs.
- What happens when the active window title is empty or contains special characters?
- What happens when multiple instances of the application are launched simultaneously? Only one instance allowed per user login - subsequent launches activate existing instance.
- What happens when the system clock is changed (time zone adjustment, daylight saving time)?
- What happens when the user is inactive for extended periods (no window changes for hours)?
- What happens when the application crashes during tracking - is data recovered?

## Requirements *(mandatory)*

### Functional Requirements

#### Onboarding & Profile Management
- **FR-001**: System MUST display a welcome screen on first launch requiring user to enter name, role, and main goal
- **FR-002**: System MUST validate that all required fields (name, role, main goal) are non-empty before proceeding
- **FR-003**: System MUST save user profile data to a local profile.json file
- **FR-004**: System MUST detect existing profile.json on subsequent launches and skip onboarding
- **FR-005**: System MUST allow users to update their profile information from within the application

#### Tracking Engine
- **FR-006**: System MUST provide a "Start Tracking" button that initiates background window monitoring
- **FR-007**: System MUST poll the active window title every 5 seconds while tracking is active
- **FR-008**: System MUST filter out browser suffixes (e.g., " - Google Chrome", " - Mozilla Firefox", " - Microsoft Edge") from window titles before logging
- **FR-009**: System MUST track windows in the background even when the application window is minimized
- **FR-010**: System MUST provide a "Stop Tracking" button that terminates the background polling
- **FR-011**: System MUST maintain a live feed on the dashboard showing the most recent window activity (e.g., last 10-20 entries)
- **FR-012**: System MUST save all tracked window titles with timestamps to logs.json

#### Dashboard & Focus Score
- **FR-013**: System MUST display a "Focus Score" metric on the dashboard
- **FR-014**: System MUST update the Focus Score by sending tracked window patterns to the AI service for analysis
- **FR-015**: System MUST display a "Live Feed" section showing real-time window activity
- **FR-016**: System MUST refresh the Live Feed within 10 seconds of window changes

#### AI Integration
- **FR-017**: System MUST provide a "Stop & Summarize" button that generates a daily summary
- **FR-018**: System MUST batch all logged activity from logs.json and send it to the AI service only when explicitly requested
- **FR-019**: System MUST display the AI-generated summary in the application interface
- **FR-020**: System MUST handle AI service failures gracefully with user-friendly error messages
- **FR-021**: System MUST preserve local logs even if AI summary generation fails
- **FR-033**: System MUST apply adaptive timeout for AI requests: 5 seconds during shutdown/sleep events, 30 seconds for manual user-initiated requests

#### Privacy & Data Storage
- **FR-022**: System MUST store all tracking data exclusively in local logs.json file
- **FR-023**: System MUST NOT send any window tracking data to external services except during explicit "Stop & Summarize" requests
- **FR-024**: System MUST ensure the AI API key is stored securely (e.g., environment variable or encrypted local storage, not hardcoded)
- **FR-025**: System MUST provide clear visual indication in the UI when tracking is active vs. inactive
- **FR-026**: System MUST provide a way for users to manually delete their tracked logs (e.g., "Clear History" button or delete logs.json file)

#### System Behavior & Instance Management
- **FR-027**: System MUST enforce single instance per user login session (background operation)
- **FR-028**: System MUST intercept system shutdown/restart/sleep events and prompt user with summary option
- **FR-029**: System MUST provide option to save work state before shutdown for recovery on next launch
- **FR-030**: System MUST display previous session's completed work on application launch
- **FR-031**: System MUST use AI to detect task accomplishments from activity patterns and display celebratory notification (star flash)
- **FR-032**: System MUST provide an options/settings menu to configure notification and intercept behaviors

### Key Entities

- **User Profile**: Represents the user's identity and goals. Attributes include name (string), role (string, e.g., "Developer", "Student"), main goal (string, free-text). Stored in profile.json. One profile per application installation.

- **Window Activity Log**: Represents discrete time-stamped observations of user activity. Each entry includes timestamp (ISO 8601), window title (string, filtered of browser suffixes), and raw window title (original unfiltered string). Collection of logs stored in logs.json. No automatic limit on number of entries - users must manually delete old logs.

- **Focus Score**: Represents a quantitative measure of user focus over a tracking session. Calculated by sending window activity patterns to the AI service for analysis and scoring. Displayed as a numeric value (scale determined by AI response, possibly 0-100). No persistent storage required - recalculated on demand from logs via AI service.

- **Daily Summary**: Represents AI-generated insights about user's activity. Attributes include summary text (string), key patterns identified (list of strings), and goal alignment assessment (string). Generated on-demand, not persisted unless explicitly saved by user.

- **Work State**: Represents the user's completed work and session state that persists across application launches. Attributes include completed tasks (list of strings), session summary (string), timestamp (ISO 8601), and streak information (count of consecutive productive sessions). Stored in work_state.json. Displayed on launch to show previous accomplishments.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the initial onboarding flow in under 2 minutes on first launch
- **SC-002**: The Live Feed displays window activity changes within 10 seconds of the user switching windows
- **SC-003**: The Focus Score updates within 30 seconds of significant changes in tracked activity patterns
- **SC-004**: Users can successfully generate an AI summary in under 15 seconds after clicking "Stop & Summarize" (assuming normal network conditions)
- **SC-005**: The application can track continuously for 8 hours without memory leaks exceeding 500MB
- **SC-006**: 95% of users can start and stop tracking without consulting documentation
- **SC-007**: No tracking data is transmitted to external services without explicit user action (Stop & Summarize)
- **SC-008**: The application recovers gracefully from system sleep/hibernation without losing tracking data
- **SC-009**: Profile data persists correctly across application restarts in 100% of cases
- **SC-010**: Users can identify their most-used applications and time distribution from the AI summary
