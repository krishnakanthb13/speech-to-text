@echo off
chcp 65001 > nul
title Handy-Groq Web Server

:: 1. Tool Check
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] ERROR: Python is not installed.
    pause
    exit /b
)

:: 2. Environment Check
set "USE_VENV=0"
:: Check for key web server dependencies: flask, flask_cors, groq, dotenv, requests, pyopenssl
python -c "import flask, flask_cors, groq, dotenv, requests, OpenSSL" >nul 2>nul
if %errorlevel% neq 0 (
    echo [i] Global web packages missing or incomplete. Using/Checking venv...
    set "USE_VENV=1"
) else (
    echo [i] Global packages found.
)

if "%USE_VENV%"=="1" (
    if not exist venv (
        echo [i] Venv not found, creating...
        python -m venv venv
        call venv\Scripts\activate
        echo [i] Installing dependencies...
        pip install -r requirements.txt
        pip install -r web_server\requirements.txt
    ) else (
        call venv\Scripts\activate
        :: Check if modules are actually installed in the venv
        python -c "import flask, flask_cors, groq, dotenv, requests, OpenSSL" >nul 2>nul
        if %errorlevel% neq 0 (
             echo [i] Updating venv dependencies...
             pip install -r requirements.txt
             pip install -r web_server\requirements.txt
        )
    )
)

:: 3. Run Server
cls
echo ===========================================
echo       🎙️  Handy-Groq Web Interface
echo ===========================================
echo Open your browser to: http://localhost:8091
echo ===========================================
cd web_server
python app.py
pause
