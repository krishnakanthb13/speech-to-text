#!/bin/bash

# --- Handy-Groq STT Launcher for Unix (Linux/macOS) ---
# Permission: Run 'chmod +x launch.sh' before executing.

APP_NAME="Handy-Groq STT"
PYTHON_CMD="python3"

# Trap exit to kill subprocesses
trap 'kill 0' SIGINT SIGTERM EXIT

clear
echo "===================================="
echo "    🎙️  $APP_NAME Launcher"
echo "===================================="

# 1. Pre-flight Checks
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "[!] Error: python3 is not installed or not in PATH."
    exit 1
fi

if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "[i] .env file not found. Creating from .env.example..."
        cp .env.example .env
        echo "[!] Please open .env and add your GROQ_API_KEY."
        read -p "Press Enter to continue..."
    else
        echo "[!] Error: .env and .env.example not found."
        exit 1
    fi
fi

# 2. Environment Check
echo "[i] Checking for required Python packages..."
if $PYTHON_CMD -c "import groq, sounddevice, pynput, numpy, scipy, pyperclip" &> /dev/null; then
    echo "[i] Global packages found."
else
    echo "[w] Global packages missing. Using virtual environment..."
    if [ ! -d "venv" ]; then
        echo "[i] Virtual environment not found. Creating one..."
        $PYTHON_CMD -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
fi

# 3. Main Menu
show_menu() {
    echo "===================================="
    echo "    1. Start Recording"
    echo "    2. Change Settings"
    echo "    3. View History"
    echo "    0. Exit"
    echo "===================================="
    read -p "Select an option (0-3): " choice
}

while true; do
    show_menu
    case $choice in
        1)
            clear
            echo "Starting $APP_NAME..."
            echo "Press the configured hotkeys to record."
            python main.py
            read -p "Press Enter to return to menu..."
            clear
            ;;
        2)
            python settings_manager.py
            ;;
        3)
            python history_viewer.py
            read -p "Press Enter to return to menu..."
            clear
            ;;
        0)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "[!] Invalid option."
            sleep 1
            clear
            ;;
    esac
done
