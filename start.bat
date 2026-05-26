@echo off
title Spam Email Classifier
setlocal enabledelayedexpansion

:: ============================================================================
::  Spam Email Classifier — One-Click Launcher for Windows
:: ============================================================================
::  This script:
::    1. Checks Python is installed
::    2. Creates a virtual environment (if missing)
::    3. Installs all dependencies
::    4. Trains models (if not already trained)
::    5. Launches the Streamlit web app (frontend + ML backend)
::    6. Opens your browser to http://localhost:8501
:: ============================================================================

:: ---------------------------------------------------------------------------
::  Step 1 — Check Python
:: ---------------------------------------------------------------------------
echo ================================================================================
echo   Spam Email Classifier - Starting Up
echo ================================================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not on PATH.
    echo   Please install Python 3.10+ from https://python.org and try again.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "pyver=%%i"
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
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo   Virtual environment created.
) else (
    echo   Virtual environment already exists.
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

echo [OK] Virtual environment activated

:: ---------------------------------------------------------------------------
::  Step 3 — Install dependencies
:: ---------------------------------------------------------------------------
echo.
echo [2/4] Installing dependencies...

:: Check if requirements are already installed by verifying a few key packages
pip show streamlit scikit-learn pandas >nul 2>&1
if %errorlevel% neq 0 (
    echo   Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install dependencies.
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
            echo [ERROR] Model training failed. Check the logs for details.
            pause
            exit /b 1
        )
        echo   Models trained successfully!
    ) else (
        echo   Skipping training. Run it later with:
        echo     python -m src.pipeline.training_pipeline
        echo.
        echo   The app will show a helpful error if no models exist.
    )
) else (
    echo   Trained models found.
)

:: ---------------------------------------------------------------------------
::  Step 5 — Launch Streamlit app (frontend + ML inference backend)
:: ---------------------------------------------------------------------------
echo.
echo [4/4] Launching web app...
echo.
echo ================================================================================
echo   App is starting! Your browser will open in a moment...
echo   If it doesn't, visit: http://localhost:8501
echo.
echo   Press CTRL+C in this window to stop the server.
echo ================================================================================
echo.

:: Open browser after a short delay (background process)
start /b "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8501"

:: Launch Streamlit (this blocks until the server stops)
python -m streamlit run app.py --server.headless true --server.port 8501

:: Keep window open on error
echo.
echo [INFO] The web app server has stopped.
pause
