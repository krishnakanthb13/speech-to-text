# 🎙️ Handy-Groq STT

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

![Handy-Groq STT](./assets/release_v0.1.16.png)

**Handy-Groq: Press, speak, and watch your thoughts turn into perfectly refined text in any application.**

A high-performance, context-aware AI voice assistant that transcribes and auto-types refined text via global hotkeys. Now supporting **Windows, Linux, and macOS**. Built with Groq's Whisper-large-v3 for near-instant speed and LLM refinement for professional results.

![Handy-Groq-STT](./assets/Handy-Groq-SST.gif)

---

## ✨ Features

- 🚀 **Extreme Speed**: Powered by Groq's Whisper-large-v3-turbo.
- 🌐 **Modern Web UI**: A beautiful, glassmorphism-styled web interface for recording and management. Now features a **Light/Dark Theme Toggle** 🌗, **History Search** 🔍, and **Spacebar Shortcut** ⌨️ to start/stop recording.
- ⏱️ **Live Elapsed Timer**: The floating widget displays elapsed recording duration in seconds (Desktop).
- 🌡️ **Temperature Control**: Configure LLM temperature (0.0 to 2.0) via CLI, Web UI slider, or `config.json` (defaults to 0.7) to adjust creativity.
- ⚙️ **Per-Profile Refinement**: Enable or disable AI refinement on a per-profile level, overriding the global setting (e.g., the Simple profile skips refinement by default).
- ℹ️ **Version Tracking**: Check version easily using `python main.py --version`.
- 📜 **Enhanced History**: View, Copy, and Delete past transcriptions. Includes **Custom Personality Badges** 🎭 and intelligent empty states 👻.
- 🧠 **Context-Aware Refinement**: Optional AI layer to fix grammar, punctuation, and "ums/ahs".
- 🎭 **Aggressive AI Personalities**: A powerful engine that completely transforms your text style. From "Robotic Log Files" to "Gen-Z Slang" or "Rage Rants" – the AI doesn't just tweak, it rewrites.
- 💾 **Personality Persistence**: AI personality sliders are saved to `localStorage` and restored on page load with validation.
- 🟠 **Visual Personality Indicator**: The AI Personality button glows orange when customized outside the default range.
- 📜 **Smart Prompt Display**: View the active system prompt in a clean, scrollable interface.
- 🛡️ **Rate Limiting**: Built-in protection against abuse with Flask-Limiter (15 requests/minute).
- 📥 **System Tray Icon**: Runs in the background with a quick-access menu (Desktop).
- 🔐 **Secure & Local**: Web server runs on HTTP/Localhost for maximum privacy and browser compatibility.
- 🏁 **Windows Auto-start**: Optional setting to launch automatically on login.
- ⌨️ **Global Hotkeys**: Uses `Ctrl + Alt + Number` combos for instant activation.
- 🪄 **Auto-Type & Copy**: Automatically types into active windows via `Ctrl+V` and copies to clipboard (Desktop).
- 🎨 **Premium Visual Widget**: A floating pill featuring vibrant emojis (Desktop).
- 🔊 **Sound Cues**: Integrated audio feedback for all states (Desktop).

---

## 🚀 Setup & Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note for macOS users:* To enable the System Tray Icon, you also need:
   ```bash
   pip install pyobjc-framework-Cocoa
   ```

2. **Configure API Key**:
   - The launcher will automatically create a `.env` file from `.env.example` if it doesn't exist.
   - Simply open the `.env` file and add your [Groq API Key](https://console.groq.com/keys).

3. **Get the Visual Widget (Optional but Recommended)**:
   - Ensure `tkinter` is installed (standard with Python on Windows).

---

## 🎮 Usage

### Launching the App
- **Windows**: Double-click **`run_groq_stt.bat`**.
- **Linux / macOS**: Run `chmod +x run_groq_stt.sh` and then **`./run_groq_stt.sh`**.

### 🌐 Web Interface (New!)
A beautiful, modern web UI for dictation, history management, and configuration.
- **Windows**: Double-click **`run_web_stt.bat`**. (Automatically cleans up port 8091 before starting).
- **Linux/macOS**: Run **`./run_web_stt.sh`**. (Automatically cleans up port 8091 before starting).
- **Access**: Open `http://localhost:8091` in your browser. (Also accessible via local network IP).

### ⌨️ Contextual Profiles (Desktop)
Hold the specific combo to record, then release to transcribe and type:

| Profile | Hotkey | Purpose |
| :--- | :--- | :--- |
| **General** | `Ctrl + Alt + 1` | Standard speech to clear text |
| **Coding** | `Ctrl + Alt + 2` | Documentation & structured code |
| **Email** | `Ctrl + Alt + 3` | Professional business email body |
| **Meeting** | `Ctrl + Alt + 4` | Summarize speech into action items |
| **Simple** | `Ctrl + Alt + 5` | Convert jargon to plain English |
| **Social** | `Ctrl + Alt + 6` | Catchy posts for LinkedIn/X |
| **Safe Exit** | `Ctrl + Alt + 0` | Stop and close the application |

### ⚙️ Settings
Access settings via the **Tray Icon** (right-click) or **CLI** (Option 2):
- Toggle **Auto-start on Windows**.
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

## 📜 License
This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](LICENSE) file for details.

---
*Inspired by @krishnakanthb13. Optimized for high-productivity workflows.*
