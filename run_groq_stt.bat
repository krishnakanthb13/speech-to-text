@echo off
chcp 65001 > nul
title Handy-Groq STT Launcher
setlocal enabledelayedexpansion

:: 1. Tool Check
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] ERROR: Python is not installed or not in PATH.
    pause
    exit /b
)

:: 2. .env Check
if not exist .env (
    if exist .env.example (
        echo [i] .env file not found. Creating from .env.example...
        copy .env.example .env >nul
        echo [!] Please open .env and add your GROQ_API_KEY.
        pause
    ) else (
        echo [!] ERROR: .env and .env.example not found!
        pause
        exit /b
    )
)

:: 3. Environment Check
set "USE_VENV=0"
python -c "import groq, sounddevice, pynput, numpy, scipy, pyperclip" >nul 2>nul
if %errorlevel% neq 0 (
    echo [w] Global packages missing. Using virtual environment...
    set "USE_VENV=1"
) else (
    echo [i] Global packages found.
)

if "%USE_VENV%"=="1" (
    if not exist venv (
        echo [i] Virtual environment not found. Creating one...
        python -m venv venv
        call venv\Scripts\activate
        echo [i] Installing dependencies...
        pip install -r requirements.txt
    ) else (
        call venv\Scripts\activate
    )
)

:menu
cls
echo ====================================
echo     🎙️  Handy-Groq STT Launcher    
echo ====================================
echo     1. Start Recording
echo     2. Change Settings
echo     3. View History
echo     0. Exit
echo ====================================
set /p choice="Select an option (0-3): "

if "%choice%"=="1" goto start_app
if "%choice%"=="2" goto settings
if "%choice%"=="3" goto history
if "%choice%"=="0" exit
goto menu

:start_app
cls
echo Starting Groq STT App...
echo Press Ctrl + Alt + 1/2/3 to record respective profiles.
python main.py
pause
goto menu

:settings
python settings_manager.py
goto menu

:history
python history_viewer.py
pause
goto menu
