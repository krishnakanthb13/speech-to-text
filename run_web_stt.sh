#!/bin/bash

# 1. Tool Check
if ! command -v python3 &> /dev/null; then
    echo "[!] ERROR: Python3 is not installed."
    exit 1
fi

# 2. Environment Check
USE_VENV=0
# Check for key web server dependencies
python3 -c "import flask, flask_cors, groq, dotenv, requests, OpenSSL" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[w] Global packages missing or incomplete. Using/Checking venv..."
    USE_VENV=1
else
    echo "[i] Global packages found."
fi

if [ "$USE_VENV" -eq 1 ]; then
    if [ ! -d "venv" ]; then
        echo "[i] Virtual environment not found. Creating one..."
        python3 -m venv venv
        source venv/bin/activate
        echo "[i] Installing dependencies..."
        pip install -r requirements.txt
        pip install -r web_server/requirements.txt
    else
        source venv/bin/activate
        # Check if packages are installed in venv
        python3 -c "import flask, flask_cors, groq, dotenv, requests, OpenSSL" >/dev/null 2>&1
        if [ $? -ne 0 ]; then
             echo "[i] Updating venv dependencies..."
             pip install -r requirements.txt
             pip install -r web_server/requirements.txt
        fi
    fi
fi

# 3. Run Server
clear
echo "==========================================="
echo "      🎙️  Handy-Groq Web Interface"
echo "==========================================="
echo "  Open your browser to: http://localhost:8091"
echo "  IMPORTANT: You will see a 'Not Secure' warning."
echo "  Click 'Advanced' -> 'Proceed to localhost (unsafe)'"
echo "==========================================="

cd web_server
python3 app.py
