# 🚀 Release Notes - Handy-Groq STT

# 🚀 **v0.1.12 — Stability, UX & Safety**

**AI personality persistence:** Personality sliders are now saved to `localStorage` and automatically restored on page load. Values are written whenever a slider changes, a preset is applied, or reset is clicked. Stored values are validated to ensure they are numbers between 0 and 100, and invalid or corrupted data safely falls back to defaults.

**AI personality indicator:** The AI Personality button now visually reflects when the personality has been customized. If any slider moves outside the default 40–60 range, the button gains an orange glow and border. The indicator updates in real time as sliders or presets change.

**Chat parameter validation:** The backend now strictly validates all personality parameters. Only the allowed keys (`humanRobot`, `factCreative`, `funnyRage`, `expertLame`, `formalSlang`) are accepted, and all values must be numbers between 0 and 100. Invalid requests are rejected with a 400 response and a descriptive error message.

**Crash-safe history deletion:** History deletion is now atomic and resilient to crashes. The server writes to a temporary file first and then uses an atomic rename to replace the original, ensuring history files can never be left in a partially written or corrupted state.

**Rate limiting:** Flask-Limiter has been added with a global limit of 15 requests per minute. The `/api/record` endpoint is explicitly protected with the same limit, using IP-based tracking via `get_remote_address` to prevent abuse and runaway clients.

---

## [v0.1.10] - THE PERSONALITY & UX UPDATE - 2026-01-28

This release focuses on **user experience** and **expression**. We've completely overhauled the Personality Engine to be more aggressive and impactful, while streamlining the Web UI for faster workflows.

### 🚀 New Features
- 🎭 **Aggressive AI Personalities**: The AI doesn't just "nudge" your text anymore—it transforms it. With our new prompt injection engine, selecting "Roast" or "Robot" will rewrite your transcript completely to match that persona.
- 📋 **Auto-Clipboard (Web)**: Transcription results are now automatically copied to your clipboard. Just hit `Ctrl+V`!
- 👻 **Smart History States**: Added playful "Ghost" empty states and new **"🎭 Custom" badges** in history logic to spot which recordings used specific personalities.

### ⚡ Improvements
- **💬 Direct Feedback**: Replaced intrusive "toast" notifications with clean, inline status messages (e.g., "Done! (Ctrl+V to paste)") that persist for 4 seconds.
- **📜 Smart Scrolling**: Added simple, native scrolling to the Prompt Display and Result areas for better readability of long texts.
- **🛡️ Robust Error Handling**: Added graceful fallbacks for history loading and network errors.

### 📚 Documentation
- **📖 Comprehensive Update**: Synced `README`, `CODE_DOCUMENTATION`, and `DESIGN_PHILOSOPHY` with the new "Aggressive Alignment" principle and Web UI features.

---


## [v0.0.8] - THE GENESIS RELEASE - 2026-01-26

This is the initial public release of **Handy-Groq STT**, the push-to-talk AI transcription companion designed to eliminate the friction between thought and text.

### 🌟 Core Features

- **🚀 Near-Instant Speed**: Powered by Groq’s `whisper-large-v3-turbo`, delivering transcriptions at hardware speeds.
- **🎨 Premium Status Pill**: A floating, glassmorphism-inspired UI widget that stays on top to show recording states with Apple-style aesthetics.
- **🧠 6 Contextual AI Profiles**: Shift between modes instantly using global hotkeys (`Ctrl + Alt + 1-6`):
    - **General**: Clean, accurate speech-to-text.
    - **Coding**: Technical documentation and code-friendly formatting.
    - **Email**: Professional tone for high-stakes communication.
    - **Meeting**: Auto-summarizes speech into minutes and action items.
    - **Simple**: Strips away jargon for plain English clarity.
    - **Social**: Catchy, emoji-aware posts for LinkedIn & X.
- **⚡ Atomic Output**: Uses a highly-optimized clipboard paste mechanism (`Ctrl+V`) for instant, single-block text insertion into any app.
- **📜 Transcription History**: Every call is logged in `history.log` with a built-in CLI `history_viewer.py` to revisit your thoughts.
- **⚙️ Settings Manager**: A robust CLI menu to hot-swap models, prompts, and hotkey configurations on the fly.
- **🌐 Cross-Platform Launchers**: Native support for Windows (`.bat`) and Unix/macOS (`.sh`) with automatic environment setup.
- **🛡️ Secure & Open**: Fully documented under GPL v3, including a security audit and contribution guidelines.

### 📋 Getting Started
1. Get your API key from [Groq Console](https://console.groq.com/).
2. Run `run_groq_stt.bat` (Windows) or `run_groq_stt.sh` (Mac/Linux).
3. Hold `Ctrl + Alt + 1` and start speaking.

---

## [v0.0.11] - THE VISUAL EXCELLENCE UPDATE - 2026-01-26

- **🎨 High-Fidelity Emojis**: Added support for vibrant, native color emojis (🎙️, 🤖, ✅) using the **Pillow** rendering engine.
- **🅰️ Premium Typography**: Switched to bold **Segoe UI** system fonts for a more polished, professional look.
- **📐 Refined Pill Layout**: Widened the status pill and optimized the layout to prevent overlap between text and the pulsing activity dot.
- **📦 Dependency Update**: Added `Pillow` to `requirements.txt` to support the new image-based UI rendering.

---

## [v0.0.15] - THE CROSS-PLATFORM & STABILITY UPDATE - 2026-01-27

This major update brings Handy-Groq STT to the system tray and introduces full macOS support for configuration, alongside significant architectural improvements.

### 🚀 New Features
- **📥 System Tray Integration**: The application now lives in your system tray (Windows & macOS). Right-click to toggle features, access settings, or exit cleanly.
- **🍎 macOS Settings Support**: Fully enabled the interactive settings menu for macOS users, allowing on-the-fly configuration of models and prompts.
- **💻 Windows Auto-Start**: Added the ability to toggle "Launch on Startup" directly from the settings menu for Windows users.

### ⚡ Improvements
- **🧵 Thread-Safe Architecture**: Refactored the core recording and UI update logic to ensure absolute stability during high-speed transcription cycles.
- **🛡️ Robust Logging**: Implemented a rotating JSONL logging system (`history.log`) to track performance and transcription history without bloating disk space.
- **🎨 UI Refinement**: Optimized the status pill layout for better cross-platform rendering and high-DPI displays.

### 📚 Documentation
- **📖 Comprehensive Guide**: Updated `README.md` and `CODE_DOCUMENTATION.md` to reflect the new system tray features and macOS installation requirements.
- **📋 Contribution Standards**: Established clear guidelines in `CONTRIBUTING.md` for community involvement.

### 🏗️ Infrastructure & Maintenance
- **🔧 Clean Shutdown**: Improved signal handling for graceful application exits, ensuring all resources are released properly.
- **📦 Dependency Management**: Updated `requirements.txt` with platform-specific notes for macOS (`pyobjc`).

---

## [v0.1.5] - THE WEB REVOLUTION & SAFETY UPDATE - 2026-01-27

This massive update introduces the **Handy-Groq Web Station**, a modern glassmorphism command center for your history and settings, alongside major security and UX improvements.

### 🚀 New Features
- **🌐 Web Interface**: A stunning new local web app (`http://localhost:8091`) powered by Flask & Waitress. Access your tools from any browser on your network.
- **🗑️ History Management**: You asked, we delivered! You can now **delete specific recordings** directly from the Web UI history modal.
- **🔐 Pragmatic Security**: Switched to HTTP for localhost (preventing scary browser warnings) while implementing XSS protection for safer viewing.
- **✨ Footer Credits**: Added `Made with 🧠, ☕, and 🤖` signature to the web interface.

### ⚡ Improvements
- **🏭 Production Server**: Migrated the web backend from Flask dev server to `Waitress`, ensuring production-grade stability and removing console warnings.
- **📉 Performance**: Optimized API to return only the last 50 history items, drastically improving load times.
- **🖱️ UX Polish**: Added `Ctrl+C` / `Escape` shortcut handlers to instantly close modals in the Web UI.
- **🎨 Visuals**: New high-quality release hero image demonstrating the Web UI.

### 📚 Documentation
- **📖 Dual-Interface Docs**: Completely rewrote `README.md` and `CODE_DOCUMENTATION.md` to cover both Desktop and Web architectures.
- **🗺️ Design Philosophy**: Added sections on "Universal Accessibility" and "Pragmatic Security".