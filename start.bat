@echo off
title Spam Email Classifier
setlocal enabledelayedexpansion

:: ============================================================================
::  Spam Email Classifier — One-Click Launcher for Windows
:: ============================================================================
::  This script:
::    1. Checks Python is installed with version >= 3.10
::    2. Creates/configures a virtual environment
::    3. Installs all dependencies (with retry on network failure)
::    4. Trains models (if not already trained)
::    5. Checks port availability before launch
::    6. Launches the Streamlit web app
::    7. Opens your browser to http://localhost:8501
:: ============================================================================

set "PORT=8501"

echo ================================================================================
echo   Spam Email Classifier - Starting Up
echo ================================================================================
echo.

:: ---------------------------------------------------------------------------
::  Step 1 — Check Python exists and version >= 3.10
:: ---------------------------------------------------------------------------

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python is not installed or not on your PATH.
    echo   Please install Python 3.10+ from https://python.org
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "pyver=%%i"

for /f "tokens=1,2 delims=." %%a in ("%pyver%") do (
    set "py_major=%%a"
    set "py_minor=%%b"
)

if %py_major% lss 3 goto :version_too_old
if %py_major% equ 3 (
    if %py_minor% lss 10 goto :version_too_old
)
goto :version_ok

:version_too_old
echo.
echo [ERROR] Python 3.10+ is required, but you have Python %pyver%.
echo   Please install a newer Python from https://python.org
echo.
pause
exit /b 1

:version_ok
echo [OK] Python %pyver% found

:: ---------------------------------------------------------------------------
::  Step 2 — Set up virtual environment
:: ---------------------------------------------------------------------------
echo.
echo [1/4] Setting up virtual environment...

if not exist ".venv\Scripts\python.exe" (
    echo   Creating virtual environment...
    python -m venv .venv
    if !errorlevel! neq 0 (
        echo.
        echo [ERROR] Failed to create virtual environment.
        echo   Possible causes:
        echo     - Insufficient disk space
        echo     - Permission restrictions on this directory
        echo     - A corrupted Python installation
        echo.
        echo   Try running: python -m venv .venv
        echo.
        pause
        exit /b 1
    )
    echo   Virtual environment created.
) else (
    echo   Virtual environment already exists.
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Verify we're inside the venv (Python 3.3+)
python -c "import sys; exit(0 if sys.prefix != sys.base_prefix else 1)" >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo [WARN] Virtual environment activation may have failed.
    echo   The .venv directory might be corrupted.
    set /p recreate_choice="  Recreate virtual environment? (Y/N, default=N): "
    if /i "!recreate_choice!"=="Y" (
        echo   Removing old virtual environment...
        rmdir /s /q .venv
        echo   Creating fresh virtual environment...
        python -m venv .venv
        if !errorlevel! neq 0 (
            echo.
            echo [ERROR] Failed to create virtual environment after retry.
            echo   Please delete the .venv folder manually and try again.
            echo.
            pause
            exit /b 1
        )
        call .venv\Scripts\activate.bat
        python -c "import sys; exit(0 if sys.prefix != sys.base_prefix else 1)" >nul 2>&1
        if !errorlevel! neq 0 (
            echo.
            echo [ERROR] Virtual environment still cannot be activated after recreation.
            echo   Try deleting the .venv folder manually and re-running.
            echo.
            pause
            exit /b 1
        )
    ) else (
        echo   Proceeding with system Python — may cause dependency conflicts.
    )
) else (
    echo [OK] Virtual environment activated
)

:: ---------------------------------------------------------------------------
::  Step 3 — Install dependencies
:: ---------------------------------------------------------------------------
echo.
echo [2/4] Installing dependencies...

python -c "import streamlit, sklearn, pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo   Installing dependencies from requirements.txt...
    
    set /a install_attempt=0
:retry_install
    set /a install_attempt+=1
    
    pip install -r requirements.txt
    if !errorlevel! neq 0 (
        if !install_attempt! lss 3 (
            echo.
            echo [WARN] Installation failed (attempt !install_attempt!/3). Retrying...
            echo   This may be a temporary network issue.
            timeout /t 3 /nobreak >nul
            goto retry_install
        )
        echo.
        echo [ERROR] Failed to install dependencies after 3 attempts.
        echo   Possible causes:
        echo     - No internet connection
        echo     - Corporate firewall / proxy blocking pip
        echo     - Insufficient disk space
        echo.
        echo   Try running: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo   Dependencies installed successfully.
) else (
    echo   Dependencies already installed.
)

:: ---------------------------------------------------------------------------
::  Step 4 — Check for trained models
:: ---------------------------------------------------------------------------
echo.
echo [3/4] Checking for trained models...

dir /b outputs\*\models\vectorizer.pkl >nul 2>&1
if %errorlevel% neq 0 (
    echo   No trained models found.
    echo   The web app requires trained models to run.
    echo   Training takes 5-10 minutes on a typical machine.
    
    set /p train_choice="  Train models now? (Y/N, default=N): "
    if /i "!train_choice!"=="Y" (
        echo.
        echo   Training models (this may take a while)...
        python -m src.pipeline.training_pipeline
        if !errorlevel! neq 0 (
            echo.
            echo [ERROR] Model training failed.
            echo   Check the logs in the outputs/ directory for details.
            echo   You can also run: python -m src.pipeline.training_pipeline
            echo.
            pause
            exit /b 1
        )
        echo   Models trained successfully!
    ) else (
        echo   Skipping training. The app will show an error if no models exist.
        echo   To train later, run: python -m src.pipeline.training_pipeline
    )
) else (
    echo   Trained models found.
    for /f "delims=" %%d in ('dir /b /ad /o-d outputs 2^>nul') do (
        set "latest_run=%%d"
        goto :found_latest
    )
:found_latest
    if defined latest_run (
        echo   Latest run: %latest_run%
    )
)

:: ---------------------------------------------------------------------------
::  Step 5 — Check port availability before launching
:: ---------------------------------------------------------------------------
echo.
echo [4/4] Launching web app...

:: Check if port 8501 is already in use
netstat -an 2>nul | findstr /C:":%PORT% " >nul
if !errorlevel! equ 0 (
    echo.
    echo [WARN] Port !PORT! is already in use — Streamlit may be running already.
    set /p port_choice="  Launch on a different port? (Y/N, default=N): "
    if /i "!port_choice!"=="Y" (
        set /p "PORT=  Enter port number (default=8501): "
        if "!PORT!"=="" set "PORT=8501"
        echo   Using port !PORT!.
    ) else (
        echo   Attempting to start on port !PORT! anyway.
        echo   To kill a process using this port:
        echo     netstat -ano ^| findstr :%PORT%
        echo     taskkill /PID ^<PID^> /F
    )
)

:: ---------------------------------------------------------------------------
::  Step 6 — Launch Streamlit and open browser
:: ---------------------------------------------------------------------------
echo.
echo ================================================================================
echo   Starting Streamlit on http://localhost:%PORT%
echo   Your browser will open in a moment...
echo.
echo   Press CTRL+C in this window to stop the server.
echo ================================================================================
echo.

:: Open browser after a short delay (background process)
start /b "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:%PORT%"

:: Launch Streamlit in the foreground (this blocks until the server stops)
python -m streamlit run app.py --server.headless true --server.port %PORT%

:: ---------------------------------------------------------------------------
::  Streamlit has stopped
:: ---------------------------------------------------------------------------
echo.
echo [INFO] The web app server has stopped.

:: Cleanup browser process that may have been left behind
taskkill /f /im "msedge.exe" /fi "WINDOWTITLE eq localhost*" >nul 2>&1
taskkill /f /im "chrome.exe" /fi "WINDOWTITLE eq localhost*" >nul 2>&1

pause
