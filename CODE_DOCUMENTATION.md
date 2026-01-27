# Code Documentation - Handy-Groq STT

## File Structure

- `main.py`: The primary application script. Handles audio recording, Groq API interaction, keyboard listeners, system tray icon, and GUI status pill.
- `config.json`: Configuration file for STT/LLM models, keyboard shortcuts (profiles), and application behavior.
- `history.log`: A JSONL log file storing transcription history. Managed by `RotatingFileHandler` (max 5MB).
- `history_viewer.py`: A utility script to view the most recent entries in `history.log`.
- `settings_manager.py`: Interactive CLI for managing configuration and Windows auto-start.
- `run_groq_stt.bat`: Windows batch file for easy launching and management.
- `run_groq_stt.sh`: Unix/macOS shell script for cross-platform launching.
- `requirements.txt`: List of Python dependencies (including `pystray`).
- `.env`: (User provided) Stores the `GROQ_API_KEY`.

## High-Level Architecture

The application operates as a persistent background service. It uses a **Main-Thread GUI** architecture where the Tkinter event loop owns the main thread for stability, while hardware listeners and API processing occur in background threads.

### Core Modules & Components

| Component | Description |
| :--- | :--- |
| `RecordingIndicator` | A custom Tkinter-based floating pill. Runs on the **Main Thread**. Updates from background threads are marshaled via `root.after`. |
| `SystemTray` | Powered by `pystray`. Provides background persistence and quick-access settings via the taskbar. |
| `GroqSTT` | The logic controller. Manages recording state and coordinates between `pynput`, `sounddevice`, and the Groq API. |
| `pynput.keyboard` | Monitors global hotkeys. Runs in a dedicated background thread. |
| `RotatingFileHandler` | Ensures `history.log` stays within a 5MB limit with automatic backups. |

## Data Flow

1. **Trigger**: User holds a profile hotkey. `pynput` triggers `start_recording` in `GroqSTT`.
2. **Audio Capture**: `sounddevice` streams audio data into a queue.
3. **End Trigger**: User releases the hotkey. UI updates to **🤖 Processing...**.
4. **Transcription**: The audio buffer is sent to Groq's Whisper API via a worker thread.
5. **Refinement**: The raw transcript is refined by a Groq LLM.
6. **Action**: The final text is copied to the clipboard and an atomic `Ctrl+V` is triggered.
7. **Logging**: The event is recorded in `history.log` via the `logging` module.

## Dependencies

- `groq`: Official Groq Python SDK.
- `pystray`: System tray icon management.
- `sounddevice`: Low-latency audio capture.
- `pynput`: Global keyboard hotkey management.
- `numpy` & `scipy`: Audio processing.
- `pyperclip`: Clipboard management.
- `tkinter`: Visual status indicator.
