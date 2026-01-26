# 🎙️ Handy-Groq STT

**Handy-Groq: Press, speak, and watch your thoughts turn into perfectly refined text in any application.**

A high-performance, context-aware AI voice assistant that transcribes and auto-types refined text via global hotkeys. Built with Groq's Whisper-large-v3 for near-instant speed and LLM refinement for professional results.

---

## ✨ Features

- 🚀 **Extreme Speed**: Powered by Groq's Whisper-large-v3-turbo.
- 🧠 **Context-Aware Refinement**: Optional AI layer to fix grammar, punctuation, and "ums/ahs".
- ⌨️ **Rare Global Hotkeys**: Uses `Ctrl + Alt + Number` combos to avoid app conflicts.
- 🪄 **Auto-Type & Copy**: Automatically types into active windows (Notepad++, IDEs, Browsers) and copies to clipboard.
- 🎨 **Premium UI Widget**: Bottom-centered floating widget with state-aware animations (Pulsing/Spinner/Checkmark).
- 🔊 **Sound Cues**: Integrated audio feedback for start, stop, success, and errors.
- 📜 **JSON History**: Every entry is logged with metadata in `history.log`.
- ⚙️ **Settings Manager**: Change models, prompts, and hotkeys via a simple CLI menu.

---

## 🚀 Setup & Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key**:
   - Rename `.env.example` to `.env`.
   - Add your [Groq API Key](https://console.groq.com/keys).

3. **Get the Visual Widget (Optional but Recommended)**:
   - Ensure `tkinter` is installed (standard with Python on Windows). If missing, run a "Modify/Repair" on your Python installation and check "tcl/tk".

---

## 🎮 Usage

Launch the app using the one-click launcher: **`run_groq_stt.bat`**.

### ⌨️ Contextual Profiles
Hold the specific combo to record, then release twice to transcribe and type:

| Profile | Hotkey | Purpose | UI Color |
| :--- | :--- | :--- | :--- |
| **General** | `Ctrl + Alt + 1` | Standard speech to clear text | 🔴 Pulsing |
| **Coding** | `Ctrl + Alt + 2` | Documentation & structured code | 🔴 Pulsing |
| **Email** | `Ctrl + Alt + 3` | Professional business email body | 🔴 Pulsing |

### ⚙️ Settings
Run **`run_groq_stt.bat`** and select **Option 2** to:
- Change STT & Refinement Models.
- Toggle Refinement, Sounds, or Logging.
- Edit Prompts and Hotkeys.

---

## 📂 Project Structure
- `main.py`: Core application and UI widget.
- `settings_manager.py`: Interactive CLI for configuration.
- `config.json`: All your custom settings.
- `history.log`: Timestamped JSON entries of all calls.
- `run_groq_stt.bat`: ModernUTF-8 launcher menu.

---
*Inspired by @[handy-cli-main]. Optimized for high-productivity workflows.*
