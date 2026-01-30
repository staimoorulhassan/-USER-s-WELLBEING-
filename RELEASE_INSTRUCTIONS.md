# 🚀 Release & Deployment Checklist

You have set up the project for success. Here are your final steps to go live.

## 1. Build the Desktop App (Windows)

We need to turn your Python code into a `WellbeingTracker.exe` file that users can download.

1. Open your terminal/command prompt.
2. Run the build script:

    ```cmd
    .\build.bat
    ```

3. Wait for the process to complete. It will create a `dist` folder.
4. Navigate to `dist\WellbeingTracker`.
5. **Test it**: Double-click `WellbeingTracker.exe` to make sure it opens.
6. **Package it**: Go back to `dist`, right-click the `WellbeingTracker` folder, and select **Send to > Compressed (zipped) folder**.
    * Name it something like `WellbeingTracker-v1.0.zip`.

## 2. Publish to GitHub

Now we host the file so users can download it.

1. Go to your GitHub Repository URL.
2. Click on **Releases** (usually on the right sidebar).
3. Click **"Draft a new release"**.
4. **Tag version**: `v1.0.0`
5. **Release title**: `v1.0 - First Public Release`
6. **Description**:
    > The first release of the AI-Powered Wellbeing Tracker.
    > * Privacy-focus tracking
    > * AI Summaries
    > * Live Focus Score
7. **Attach binaries**: Drag and drop your `WellbeingTracker-v1.0.zip` file here.
8. Click **Publish release**.

## 3. Deploy Marketing Page (Vercel)

We created a landing page (`public/index.html`) to give you a "Demo Link".

1. Go to your Vercel Dashboard.
2. If you haven't connected the repo yet:
    * Click "Add New..." > "Project".
    * Import your `wellbeing` repository.
    * **Framework Preset**: Select "Other" (or leave it; Vercel usually auto-detects HTML).
    * **Root Directory**: Leave as `./`.
    * Click **Deploy**.
3. If already deployed:
    * Vercel might have failed the *previous* build (Python error).
    * Go to the deployment, click **"Redeploy"** (so it picks up the new `public/index.html` and `vercel.json`).
4. Once green, copy the **Domain** (e.g., `wellbeing-tracker.vercel.app`).

## 4. Connect the Two

1. Copy your **Vercel Domain** link.
2. Go back to your GitHub Repo "About" section (right sidebar) and paste the link there as the "Website".
3. Now you have:
    * A **Demo Link** (Vercel Website) to share on social media.
    * A **Download Link** (GitHub Release) for people to actually use the app.

🎉 **You are done!**
