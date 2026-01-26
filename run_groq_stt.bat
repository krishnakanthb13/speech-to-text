@echo off
chcp 65001 > nul
title Groq Speech-to-Text
cd /d "%~dp0"

echo Checking dependencies...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b
)

if not exist .env (
    echo .env file not found! 
    echo Please copy .env.example to .env and add your GROQ_API_KEY.
    pause
    exit /b
)

:menu
cls
echo ==================================================
echo         🎙️  HANDY-GROQ STT LAUNCHER
echo ==================================================
echo     1. START RECORDING
echo     2. CHANGE SETTINGS
echo     3. VIEW HISTORY
echo     0. EXIT
echo ==================================================
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
