# Code Documentation - Handy-Groq STT

## File Structure

- `main.py`: The primary application script. Handles audio recording, Groq API interaction, keyboard listeners, and GUI status pill.
- `config.json`: Configuration file for STT/LLM models, keyboard shortcuts (profiles), and application behavior.
- `history.log`: A JSONL log file storing transcription history (timestamp, profile, raw text, refined text).
- `history_viewer.py`: A utility script to view the most recent entries in `history.log`.
- `settings_manager.py`: (Internal/Future) script for managing configuration.
- `run_groq_stt.bat`: Windows batch file for easy launching and management.
- `run_groq_stt.sh`: Unix/macOS shell script for cross-platform launching.
- `requirements.txt`: List of Python dependencies.
- `.env`: (User provided) Stores the `GROQ_API_KEY`.

## High-Level Architecture

The application operates as a background service that listens for specific global hotkeys. It uses a multi-threaded approach to ensure the UI remains responsive while processing audio and API requests.

### Core Modules & Components

| Component | Description |
| :--- | :--- |
| `RecordingIndicator` | A custom Tkinter-based minimal box widget that floats on top of other windows to show the current state (Listening, Processing, Done). |
| `GroqSTT` | The main logic controller. Manages state, audio buffers, and coordinates between hardware and API. |
| `pynput.keyboard` | Monitors global key presses to trigger actions. |
| `sounddevice` | Captures raw audio from the default microphone. |
| `Groq API` | Performs Whisper-based transcription and Llama-based text refinement. |

## Data Flow

1. **Trigger**: User holds a configured Profile hotkey (e.g., `Ctrl+Alt+1`).
2. **Audio Capture**: `sounddevice` streams audio data into a queue.
3. **End Trigger**: User releases the hotkey.
4. **Transcription**: The audio buffer is converted to a WAV in memory and sent to Groq's Whisper API.
5. **Refinement**: The raw transcript is sent to a Groq LLM with a profile-specific prompt for cleaning and formatting.
6. **Action**: The final text is copied to the clipboard and "pasted" into the active application using a simulated `Ctrl+V`.
7. **Logging**: The event is recorded in `history.log`.

## Dependencies

- `groq`: Official Groq Python SDK.
- `sounddevice`: For low-latency audio capture.
- **Cross-Platform**: Optimized for Windows, with compatibility for Linux and macOS via a dedicated shell launcher and `pynput` keyboard handling.
- `numpy` & `scipy`: For handling audio arrays and conversions.
- `python-dotenv`: To manage API keys securely.
- `pyperclip`: For clipboard management.
- `tkinter`: (Standard Library) For the visual status indicator.
