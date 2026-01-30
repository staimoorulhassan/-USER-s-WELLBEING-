@echo off
echo ===================================================
echo   Building Wellbeing Desktop Tracker Executable
echo ===================================================
echo.

:: 1. Setup Environment
echo [1/4] Setting up build environment...
if not exist "venv" (
    echo Error: venv not found. Please run setup first.
    pause
    exit /b 1
)
call venv\Scripts\activate

:: 2. Install PyInstaller
echo [2/4] Installing PyInstaller...
pip install pyinstaller

:: 3. Clean previous builds
echo [3/4] Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "WellbeingTracker.spec" del "WellbeingTracker.spec"

:: 4. Build Executable
echo [4/4] Building Executable (This may take a minute)...
:: --noconfirm: overwrite setup
:: --onedir: folder output (faster startup than onefile)
:: --windowed: no console window
:: --name: Output name
:: --collect-all: Ensure customtkinter assets are included
pyinstaller --noconfirm --onedir --windowed --name "WellbeingTracker" --collect-all customtkinter src/main.py

echo.
echo ===================================================
if exist "dist\WellbeingTracker\WellbeingTracker.exe" (
    echo   BUILD SUCCESSFUL!
    echo   Executable location: dist\WellbeingTracker\WellbeingTracker.exe
    echo.
    echo   To deploy: Zip the 'dist\WellbeingTracker' folder and share it.
) else (
    echo   BUILD FAILED. Check errors above.
)
echo ===================================================
pause
