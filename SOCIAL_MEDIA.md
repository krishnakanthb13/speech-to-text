# 🚀 Product Launch Announcements - Handy-Groq STT

## 👔 LinkedIn (v0.1.16 Update)
**Title: Accessibility, Granular Control & centralizing config: Handy-Groq STT v0.1.16 🎙️**

We just pushed the **v0.1.16** update to **Handy-Groq STT**—our local push-to-talk speech-to-text application with context-aware AI refinement. 

This release focuses on giving users complete control over how the AI processes their speech, and making the Web UI highly accessible.

**What's New:**
🌗 **Light/Dark Mode Toggle**: A fully responsive Light Mode style for those who prefer high-contrast, daytime themes.
🌡️ **Temperature Slider**: Control the LLM temperature (0.0 to 2.0) directly from the Web UI or CLI. Fine-tune between raw, deterministic correction (low temp) and creative rewriting (high temp).
⚙️ **Per-Profile AI Refinement**: You can now toggle refinement at the profile level. The "Simple" profile now skips AI processing entirely, while other profiles keep it active.
⏱️ **Live Elapsed Timer**: The desktop widget now shows the exact duration of your recording in real-time, helping you track length.
🔍 **History Search**: Search through past transcripts instantly by profile, raw text, or refined text.
⌨️ **Keyboard Navigation**: Press spacebar to start/stop dictation; use Escape or Ctrl+C to close modals.

Behind the scenes, we refactored the backend settings into a centralized `config_utils.py` module with atomic writes and automatic `.bak` recovery to prevent config corruption.

Check out the release: [github.com/krishnakanthb13/speech-to-text](https://github.com/krishnakanthb13/speech-to-text)

#AI #SpeechToText #OpenSource #Productivity #DeveloperTools #Whisper #Llama

---

## 🐦 X / Twitter (v0.1.16 Update)
🌗 Theme support & real-time search! Handy-Groq STT v0.1.16 is out!

🎙️ Live elapsed timer on the Tkinter widget
🌡️ LLM temperature slider (0.0 - 2.0)
⚙️ Per-profile refinement toggles (skip AI on simple notes)
⌨️ Keyboard shortcuts: Spacebar to record, Esc to close modals

Check it out: [github.com/krishnakanthb13/speech-to-text] #BuildInPublic #OpenSource #AI

---

## 🤝 Reddit (v0.1.16 Update - r/webdev / r/SideProject / r/selfhosted)
**Title: [Showcase] I added Light/Dark theme support, a live recording timer, and per-profile AI temperature sliders to my open-source push-to-talk STT tool**

Hey guys! I recently updated **Handy-Groq STT** to **v0.1.16**.

For those unfamiliar, it's a lightweight desktop widget (Tkinter) and localhost Web UI (Flask + Waitress) that acts as a global voice-to-text assistant. Hold a hotkey (or press spacebar in the web view), talk, and it instantly transcribes and types refined text into any active app using Groq (Whisper-large-v3 + Llama-3.3).

**New features in v0.1.16:**
*   **🌗 Web UI Light Theme**: Added full light/dark glassmorphism theme support with persistence in `localStorage`.
*   **⏱️ Live Duration Counter**: The Tkinter floating indicator widget now updates every 100ms to show the exact duration of the ongoing recording.
*   **🌡️ Temperature Slider**: Exposed temperature parameters (0.0 to 2.0) to configure LLM creativity.
*   **⚙️ Granular Profile Refinement**: Toggles can override global settings per-profile (so "Simple mode" skips AI refinement entirely).
*   **🔍 History Search**: Fully reactive search filter on the frontend cache.

**Technical Refactoring:**
To support safe multi-process reads/writes (desktop GUI, CLI settings, and Flask server), I centralized settings into an atomic, transactional file manager (`config_utils.py`) that uses `fsync` and `.bak` rollback procedures if a crash occurs mid-write.

Repo link: [github.com/krishnakanthb13/speech-to-text](https://github.com/krishnakanthb13/speech-to-text)

I'd love to hear your thoughts on custom prompts and profiles!

---

## 👔 LinkedIn (v0.1.10 Update)
**Title: Getting Aggressive with AI Expressions: Handy-Groq v0.1.10 🎭**

We just pushed a fascinating update to **Handy-Groq STT**.

When users asked for "Funny" or "Formal" modes, the AI sometimes played it too safe. In **v0.1.10**, we implemented an **Aggressive Prompt Engine**.

Now, if you ask for a "Roast", you don't just get a snarky comment—the AI completely rewrites your text into a full-blown roast. Same for "Robot Mode", "Gen-Z Slang", and more.

**New UX Features:**
*   📋 **Auto-Clipboard**: Web transcriptions are now instantly copied. Just talk and paste using `Ctrl+V`.
*   👻 **Smart UI**: Playful empty states and new "Custom Personality" badges in your history.
*   ⚡ **Direct Feedback**: Removed clutter (toasts) for cleaner, faster status updates.

Check out the "Aggressive Mode" in action: [github.com/krishnakanthb13/speech-to-text](https://github.com/krishnakanthb13/speech-to-text)

#AI #PromptEngineering #UX #OpenSource #Groq

---

## 🐦 X / Twitter (v0.1.10 Thread)
1/5 🎭 THE PERSONALITY UPDATE! **Handy-Groq v0.1.10** is out, and it's got an attitude problem (in a good way).

We overhauled the Personality Engine. It’s no longer polite suggestions—it’s **Aggressive Instructions**. 😤

2/5 Select "Roast" mode? The AI will tear your transcript apart. 
Select "Robot"? You get cold, hard logic logs. 🤖
Select "Gen-Z"? No cap fr fr. 🧢

It completely rewrites your text based on the sliders you choose.

3/5 📋 **Auto-Clipboard**:
We killed the extra click. Transcriptions in the Web UI are now instantly copied to your clipboard. 

Recording -> Silence -> `Ctrl+V`. That's the flow. ⚡

4/5 👻 **UX Polish**:
- "Ghost" states for empty history.
- "Custom" badges for personality-tweaked clips.
- Native scrolling for long texts.

5/5 Get the update and try the new personalities:
[github.com/krishnakanthb13/speech-to-text]

#BuildInPublic #AI #Groq #OpenSource #DevTools

---


## 👔 LinkedIn Launch
**Title: Say Hello to Handy-Groq STT: The Push-to-Talk AI Workspace Companion 🎙️**

I’m thrilled to announce the release of **Handy-Groq STT** v0.1.0! 🚀

If you’ve ever found traditional voice typing too slow or clunky for professional work, this is for you. We’ve built a "Zero Friction" experience that turns your voice into refined, context-aware text instantly.

**What's new in v0.1.0?**
- 📥 **System Tray Integration**: Now runs in the background with a sleek tray icon for quick access to settings and toggles.
- 🍎 **Full macOS Support**: Interactive settings and optimized performance for Mac users.
- 🧵 **Stability First**: Refactored thread-safe architecture for a crash-free experience.
- 🛡️ **Managed Logs**: Automatic history rotation to keep your workspace clean.

**Core Features:**
- 🏎️ **Extreme Speed**: Powered by Groq’s Whisper-large-v3-turbo.
- 🎨 **Beauty**: A sleek, floating status pill with high-fidelity emojis and pulsing animations.
- 🧠 **Context**: 6 specialized modes for Coding, Emails, Meetings, and more.
- ⚡ **Magic**: It doesn't just type; it "pastes" refined results into ANY app you're using.

Open Source. Privacy Focused. Speed Optimized.

Check out the launch on GitHub: [github.com/krishnakanthb13/speech-to-text](https://github.com/krishnakanthb13/speech-to-text)

#AI #Launch #OpenSource #Productivity #SpeechToText #DevTools #Groq #BuildInPublic

---

## 🤝 Reddit (r/MachineLearning / r/SideProject / r/Productivity)
**Title: [Showcase] I built Handy-Groq: A push-to-talk AI assistant that now lives in your system tray and supports macOS!**

Hey everyone! I just pushed a major update (**v0.1.0**) to **Handy-Groq STT**.

The goal was simple: I wanted a global hotkey that I could hold, talk to, and have the *perfect* version of that speech appear in my IDE or Email instantly.

**What's new:**
- Added a **System Tray Icon** (pystray) for better background management.
- Fully enabled **macOS support** for the interactive settings menu.
- Optimized the **Tkinter status pill** for high-DPI displays.
- Improved **Thread Safety** for more reliable long-term usage.

**Key Tech:**
- **Inference**: Whisper-large-v3-turbo + Llama-3.3-70b via Groq API.
- **UI**: Custom Tkinter canvas with high-DPI vector graphics.
- **Control**: `pynput` for global listeners.
- **OS**: Unified launchers for Windows (.bat) and Unix/macOS (.sh).

It’s completely free (GPL v3). I'm looking for feedback on more refined prompts for specific workflows!

Repo: [github.com/krishnakanthb13/speech-to-text](https://github.com/krishnakanthb13/speech-to-text)

---

## 🐦 X (Twitter) Launch Thread
1/7 🚀 THE CROSS-PLATFORM UPDATE IS HERE! Introducing **Handy-Groq STT** (v0.1.0). Now with System Tray support and full macOS compatibility! 🎙️🔥

2/7 Why use it? High-speed transcription + context-aware refinement. 🧠
Hold a hotkey -> Speak technical jargon -> Release -> Get perfectly formatted Documentation in your IDE instantly. ⚡✨

3/7 New in v0.1.0:
📥 System Tray Icon for easy control.
🍎 Native macOS settings support.
🧵 Refactored core for rock-solid stability.
🛡️ Automatic log rotation.

4/7 It comes with 6 specialized "Thought Profiles":
- 🛠️ Coding
- ✉️ Email
- 🤝 Meeting Minutes
- 📱 Social Media
- 🧹 Simple English
- 🎧 General

5/7 🎨 Look at that UI! A custom floating status pill with Apple-style aesthetics, pulsing animations, and full 4K support. It feels like hardware.

6/7 Built for speed on @GroqInc. Built for security with local logs and .env key management. Now truly cross-platform. 🌍

7/7 Check out the code and start speaking:
[github.com/krishnakanthb13/speech-to-text]

#BuildInPublic #AI #Groq #OpenSource #Productivity #Python

---

## 👔 LinkedIn (v0.1.5 Update)
**Title: The Web Station Arrives! Handy-Groq v0.1.5 🌐**

I’m excited to share the biggest update yet to **Handy-Groq STT**. 

We’ve moved beyond just a desktop tool. **v0.1.5** introduces a full-fledged **Local Web Interface**, allowing you to manage your transcription history and adjust settings from a beautiful glassmorphism dashboard.

**What's New per Request:**
*   🗑️ **History Management**: Delete specific recordings instantly (Web UI).
*   📉 **Performance**: 10x faster history loading with optimized pagination.
*   🏭 **Production Ready**: Now runs on a robust Waitress server for absolute stability.
*   🔐 **Safe**: Enhanced security with XSS protection and cleaner localhost handling.

A huge thanks to the community for the feedback on the History features! 

Check out the new Web UI: [github.com/krishnakanthb13/speech-to-text](https://github.com/krishnakanthb13/speech-to-text)

#AI #WebDev #Flask #Groq #OpenSource

---

## 🐦 X / Twitter (v0.1.5 Thread)
1/5 🌐 THE WEB UPDATE IS LIVE! **Handy-Groq v0.1.5** brings a beautiful Local Web Station to your workflow.

Now you can manage your dictation history, copy old transcripts, and configure your AI models from a stunning Glass UI in your browser. ✨

2/5 🗑️ **Trash It**: By popular demand, you can now DELETE individual recordings from your history. No more clutter.

3/5 ⚡ **Speed & Safety**:
- Switched to `Waitress` production server 🏭
- 10x faster history loading 📉
- Enhanced XSS protection 🛡️

4/5 📱 **Mobile Access**: Because it runs on your local network, you can open the Web UI on your phone and turn it into a high-quality dictation mic for your PC! 🎙️

5/5 Get the update and see the new visuals:
[github.com/krishnakanthb13/speech-to-text]

#BuildInPublic #AI #Python #Flask