@echo off
cd /d "%~dp0"
title Modernism Feature Detector

if not exist "venv\Scripts\python.exe" (
    echo First-time setup, this takes about 2 minutes...
    py -m venv venv
    if errorlevel 1 (
        python -m venv venv
        if errorlevel 1 (
            echo Python was not found. Install Python from python.org and tick 'Add python.exe to PATH'.
            pause
            exit /b 1
        )
    )
    "venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Package installation failed. Please check your internet connection and try again.
        rmdir /s /q venv
        pause
        exit /b 1
    )
)

if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
    if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit"
    (
        echo [general]
        echo email = ""
    ) > "%USERPROFILE%\.streamlit\credentials.toml"
)

echo Starting the app... your browser will open. Keep this window open while you use the app; close it to stop the app.
set MODERNISM_DESKTOP=1
"venv\Scripts\python.exe" -m streamlit run app.py --browser.gatherUsageStats false
pause
