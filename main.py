import os
import sys
import time
import queue
import threading
import json
import math
import numpy as np
import sounddevice as sd
from groq import Groq
from dotenv import load_dotenv
from pynput import keyboard
import scipy.io.wavfile as wavfile
from PIL import Image, ImageDraw, ImageFont, ImageTk
import logging
from logging.handlers import RotatingFileHandler

try:
    import ctypes
    try:  # Windows 8.1+
        # PROCESS_PER_MONITOR_DPI_AWARE = 2
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except AttributeError:  # Windows Vista/7
        ctypes.windll.user32.SetProcessDpiAwareness(1)
except Exception:
    pass  # DPI awareness is not critical

try:
    import tkinter as tk
    from tkinter import font as tkfont
    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False

import pyperclip
import winsound
from datetime import datetime
import pystray
import settings_manager

# Load environment variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
load_dotenv()

ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Configure Logging
log_formatter = logging.Formatter('%(message)s')
log_handler = RotatingFileHandler("history.log", maxBytes=5*1024*1024, backupCount=2, encoding='utf-8')
log_handler.setFormatter(log_formatter)
logger = logging.getLogger("HandyGroq")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

class RecordingIndicator:
    def __init__(self):
        self.root = None
        self.status_dot = None
        self.label = None
        self.visible = False
        self.state = "idle"
        self.animation_id = None
        self.dot_pulse = 0
        self.emoji_cache = {}
        
        if TK_AVAILABLE:
            try:
                self.root = tk.Tk()
                self.root.overrideredirect(True)
                self.root.attributes("-topmost", True)
                self.root.attributes("-alpha", 0.90)
                # Hide initially
                self.root.withdraw()
                self._create_layout()
            except Exception as e:
                print(f"[WARN] Tkinter Init Failed: {e}")
                self.root = None
        else:
            print("[INFO] Tkinter not found. Visual indicator disabled.")

    def _thread_safe(self, func, *args, **kwargs):
        """Marshal UI calls to the main thread."""
        if self.root:
            self.root.after(0, lambda: func(*args, **kwargs))

    def show(self, text="Listening...", state="recording"):
        self._thread_safe(self._show_impl, text, state)

    def _show_impl(self, text, state):
        if not self.root: return
        self._update_state(state, text)
        self.root.deiconify()
        self.visible = True
        self._pulse()

    def hide(self):
        self._thread_safe(self._hide_impl)

    def _hide_impl(self):
        if not self.root: return
        self.state = "idle"
        # after_cancel is tricky if ID is stale, but usually safe to ignore errors
        if self.animation_id:
            try: self.root.after_cancel(self.animation_id)
            except: pass
            self.animation_id = None
        self.root.withdraw()
        self.visible = False

    def update_text(self, text, state=None):
        self._thread_safe(self._update_text_impl, text, state)

    def _update_text_impl(self, text, state):
        if state:
            self._update_state(state, text)

    def _create_layout(self):
        """Build the UI elements inside the existing root."""
        # Transparent background key
        bg_color = "#1e1e1e" # Dark background
        transparent_key = "#000001"
        
        self.root.configure(bg=transparent_key)
        self.root.attributes("-transparentcolor", transparent_key)
        
        # Size and position
        width, height = 230, 44
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = screen_height - 120
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg=transparent_key, highlightthickness=0)
        self.canvas.pack()
        
        # 1. Basic Box
        self.box_id = self.canvas.create_rectangle(
            2, 2, width-2, height-2,
            fill=bg_color,
            outline="white",
            width=2
        )
        
        # 2. Status Label
        self.label = tk.Label(
            self.root,
            bg=bg_color,
            borderwidth=0,
            highlightthickness=0
        )
        self.label.place(x=18, rely=0.5, anchor=tk.W)

        # 3. Status Dot
        self.dot_id = self.canvas.create_oval(
            width - 28, height//2 - 4, 
            width - 20, height//2 + 4, 
            fill="white", outline=""
        )

    def _update_state(self, state, profile_name=None):
        self.state = state
        if not getattr(self, 'canvas', None): return
        
        states = {
            "recording": ("🎙", "Listening", "#ff4444"),
            "processing": ("🤖", "Processing...", "#ffbb00"),
            "typing": ("✅", "Done...", "#00cc00")
        }
        emoji, text, color = states.get(state, ("?", "...", "white"))
        
        if state == "recording" and profile_name:
            formatted_profile = profile_name.strip().capitalize()
            if formatted_profile != "Listening":
                text = f"Listening ({formatted_profile})"
            else:
                text = "Listening..."

        try:
            full_text = f"{emoji} {text}"
            if full_text not in self.emoji_cache:
                img_w, img_h = 600, 100
                img = Image.new('RGBA', (img_w, img_h), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                try: 
                    emoji_font = ImageFont.truetype("seguiemj.ttf", 48)
                    text_font = ImageFont.truetype("seguisb.ttf", 40)
                except: 
                    emoji_font = text_font = ImageFont.load_default()
                
                draw.text((15, img_h//2), emoji, font=emoji_font, fill=color, anchor="lm", embedded_color=True)
                draw.text((90, img_h//2), text, font=text_font, fill=color, anchor="lm")
                
                img = img.resize((170, 34), Image.Resampling.LANCZOS)
                self.emoji_cache[full_text] = ImageTk.PhotoImage(img)
            
            if hasattr(self, 'label'):
                self.label.config(image=self.emoji_cache[full_text])
                self.label.image = self.emoji_cache[full_text]
        except Exception as e:
            if hasattr(self, 'label'):
                self.label.config(text=f"{emoji} {text}", fg=color, image='')

        self.canvas.itemconfig(self.box_id, outline=color)

        if state == "typing":
            self.canvas.itemconfig(self.dot_id, state='hidden')
        else:
            self.canvas.itemconfig(self.dot_id, state='normal')
            self.canvas.itemconfig(self.dot_id, fill=color)

    def _pulse(self):
        if not self.visible or self.state != "recording": return
        self.dot_pulse = (self.dot_pulse + 1) % 2
        base_color = "#ff4444"
        pulse_color = "white" if self.dot_pulse == 0 else base_color
        
        if self.canvas and self.dot_id:
             self.canvas.itemconfig(self.dot_id, fill=pulse_color)
             
        self.animation_id = self.root.after(500, self._pulse)

    def start_loop(self):
        if self.root:
            print("[INFO] Starting UI Mainloop...")
            self.root.mainloop()

class SystemTray:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self.running = False

    def run(self):
        self.running = True
        icon_path = os.path.join(ASSETS_DIR, "main.png")
        try:
            image = Image.open(icon_path)
        except Exception:
            image = Image.new('RGB', (64, 64), color = 'red')

        menu = pystray.Menu(
            pystray.MenuItem("Refinement", self.toggle_refinement, checked=lambda item: self.app.config.get('refinement_enabled', False)),
            pystray.MenuItem("Sounds", self.toggle_sounds, checked=lambda item: self.app.config.get('play_sounds', True)),
            pystray.MenuItem("Auto-start", self.toggle_autostart, checked=lambda item: settings_manager.is_autostart_enabled()),
            pystray.MenuItem("Open Settings", self.open_settings),
            pystray.MenuItem("Exit", self.exit_app)
        )
        self.icon = pystray.Icon("HandyGroqSTT", image, "Handy Groq STT", menu)
        self.icon.run()

    def toggle_refinement(self, icon, item):
        self.app.config['refinement_enabled'] = not self.app.config['refinement_enabled']
        self.app.save_config()

    def toggle_sounds(self, icon, item):
        self.app.config['play_sounds'] = not self.app.config.get('play_sounds', True)
        self.app.save_config()

    def toggle_autostart(self, icon, item):
        current = settings_manager.is_autostart_enabled()
        settings_manager.set_autostart(not current)

    def open_settings(self, icon, item):
        if os.name == 'nt':
            # Use sys.executable to ensure we use the same python
            # Quote the executable path in case of spaces
            cmd = f'"{sys.executable}" settings_manager.py'
            os.system(f'start "Handy Groq Settings" cmd /k "{cmd}"')
        else:
            print("Settings menu only supported via terminal on this platform.")

    def exit_app(self, icon, item):
        self.icon.stop()
        self.app.stop_app()

class GroqSTT:
    def __init__(self, indicator):
        self.indicator = indicator
        self.load_config()
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("\n[!] ERROR: GROQ_API_KEY not found in .env file.")
            exit(1)
        
        self.client = Groq(api_key=self.api_key)
        self.sample_rate = 16000
        self.channels = 1
        self.recording = False
        self.audio_queue = queue.Queue()
        self.audio_data = []
        self.keyboard_controller = keyboard.Controller()
        
        self.check_microphone()
        self.current_keys = set()
        self.active_profile = None
        
        # Initialize listener but don't start yet
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        
        self._print_banner()

    def start(self):
        """Starts background threads (Listener, Tray)."""
        # Start Keyboard Listener (non-blocking mode)
        self.listener.start()
        
        # Start System Tray (in background thread)
        self.tray = SystemTray(self)
        self.tray_thread = threading.Thread(target=self.tray.run, daemon=True)
        self.tray_thread.start()

    def save_config(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=4)

    def stop_app(self):
        print("\nStopping application...")
        self.indicator.hide()
        if self.recording:
            self.stop_recording()
        # Force exit to kill all threads including mainloop
        os._exit(0)

    def _print_banner(self):
        print("\n" + "="*50)
        print("   🎙️  GROQ ULTIMATE SPEECH-TO-TEXT")
        print("="*50)
        print(f"  STT Model   : {self.config['stt_model']}")
        print(f"  Refinement  : {'✅ Enabled' if self.config['refinement_enabled'] else '❌ Disabled'}")
        print(f"  Action Mode : {self.config.get('action_mode', 'type').upper()}")
        print("\n  🚀 READY! INSTRUCTIONS:")
        for p in self.config['profiles']:
            keys = " + ".join(p['hotkey']).upper()
            print(f"  - [{p['name']}] : Press & Hold {keys}")
        print(f"  - [SAFE EXIT] : Press Ctrl + Alt + 0")
        print("-" * 50)
        print("  Logs will be stored in: history.log")
        print("=" * 50 + "\n")

    def load_config(self):
        config_path = "config.json"
        with open(config_path, "r") as f:
            self.config = json.load(f)
        
        for profile in self.config['profiles']:
            profile['key_names'] = [k.lower().strip() for k in profile['hotkey']]
        self.debug_keys = self.config.get("debug_keys", False)

    def play_sound(self, sound_type):
        if not self.config.get('play_sounds', True):
            return
        try:
            if sound_type == "start": winsound.Beep(600, 80)
            elif sound_type == "stop": winsound.Beep(450, 80)
            elif sound_type == "success": winsound.Beep(900, 120)
            elif sound_type == "error": winsound.Beep(200, 400)
        except Exception:
            pass

    def check_microphone(self):
        try:
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            if not input_devices:
                print("[!] WARNING: No microphone detected.")
                return False
            return True
        except Exception as e:
            print(f"[!] ERROR: Audio query failed: {e}")
            return False

    def _audio_callback(self, indata, frames, time, status):
        if self.recording:
            self.audio_queue.put(indata.copy())

    def start_recording(self):
        if self.recording:
            return
        try:
            self.stream = sd.InputStream(callback=self._audio_callback, samplerate=self.sample_rate, channels=self.channels)
            self.stream.start()
        except Exception as e:
            print(f"\n[!] Mic access failed: {e}")
            self.play_sound("error")
            self.indicator.show("⚠️ MIC ERROR", "idle")
            threading.Timer(2.0, self.indicator.hide).start()
            self.active_profile = None
            return

        profile_name = self.active_profile['name'] if self.active_profile else "General"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Listening ({profile_name})...", end="", flush=True)
        self.recording = True
        self.play_sound("start")
        self.indicator.show(f"{profile_name.upper()}", "recording")
        self.audio_data = []
        while not self.audio_queue.empty(): self.audio_queue.get()

    def stop_recording(self):
        if not self.recording: return None
        self.recording = False
        self.play_sound("stop")
        self.indicator.update_text("PROCESSING...", "processing")
        self.stream.stop()
        self.stream.close()
        
        while not self.audio_queue.empty(): self.audio_data.append(self.audio_queue.get())
        if not self.audio_data:
            print(" No audio captured.")
            self.indicator.hide()
            self.active_profile = None
            return None
        return np.concatenate(self.audio_data)

    def groq_request_with_retry(self, func, *args, **kwargs):
        retries = self.config.get('rate_limit_retries', 3)
        wait = self.config.get('rate_limit_wait_seconds', 2)
        for i in range(retries):
            try: return func(*args, **kwargs)
            except Exception as e:
                if "rate_limit" in str(e).lower() and i < retries - 1:
                    print(f"\n[Rate Limit] Retrying in {wait}s...")
                    time.sleep(wait); continue
                raise e
        return None

    def transcribe_audio(self, audio_data):
        temp_filename = "temp_recording.wav"
        wavfile.write(temp_filename, self.sample_rate, (audio_data * 32767).astype(np.int16))
        try:
            def call_stt():
                 with open(temp_filename, "rb") as file:
                    return self.client.audio.transcriptions.create(file=(temp_filename, file.read()), model=self.config['stt_model'])
            trans = self.groq_request_with_retry(call_stt)
            return trans.text.strip()
        except Exception as e: print(f" Transcription fail: {e}"); self.play_sound("error"); return None
        finally:
            if os.path.exists(temp_filename): os.remove(temp_filename)

    def refine_text(self, text):
        if not self.config['refinement_enabled']: return text
        prompt = self.active_profile['prompt'] if self.active_profile else "Refine text."
        try:
            def call_refinement():
                return self.client.chat.completions.create(
                    model=self.config['refinement_model'],
                    messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}]
                )
            res = self.groq_request_with_retry(call_refinement)
            return res.choices[0].message.content.strip()
        except Exception as e: print(f" Refinement fail: {e}"); return text

    def perform_action(self, text, raw_text):
        if not text: return
        mode = self.config.get('action_mode', 'type')
        
        # Always copy to clipboard first
        pyperclip.copy(text)
        
        if mode in ["type", "type_and_copy"]:
            self.indicator.update_text("Done", "typing")
            # Safety delay to ensure physically held keys are released
            time.sleep(0.3)
            # Use Ctrl+V to paste (instant, atomic output)
            with self.keyboard_controller.pressed(keyboard.Key.ctrl):
                self.keyboard_controller.tap('v')
        
        self.log_to_file(raw_text, text)
        self.play_sound("success")

    def log_to_file(self, raw, refined):
        try:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prof = self.active_profile['name'] if self.active_profile else "General"
            log_entry = {
                "timestamp": ts,
                "profile": prof,
                "raw_text": raw,
                "refined_text": refined,
                "stt_model": self.config['stt_model'],
                "refinement_model": self.config['refinement_model']
            }
            # Logger is configured to write just the message (JSON)
            logger.info(json.dumps(log_entry))
        except Exception as e: print(f"Logging error: {e}")

    def _get_key_name(self, key):
        """Unified key naming for both special keys and character keys."""
        try:
            if hasattr(key, 'name') and key.name:
                name = key.name
                if name == 'ctrl': return 'ctrl_l'
                if name == 'alt': return 'alt_l'
                if name == 'shift': return 'shift_l'
                return name
            if hasattr(key, 'char') and key.char:
                return key.char.lower()
            
            s = str(key).lower().strip("'" ).strip('"')
            if 'key.' in s:
                s = s.replace('key.', '').strip()
            
            numpad_map = {
                '<96>': '0', '<97>': '1', '<98>': '2', '<99>': '3',
                '<100>': '4', '<101>': '5', '<102>': '6', '<103>': '7',
                '<104>': '8', '<105>': '9'
            }
            return numpad_map.get(s, s)
        except Exception: return str(key).lower()

    def on_press(self, key):
        name = self._get_key_name(key)
        self.current_keys.add(name)
        
        if name == 'alt_gr':
            self.current_keys.add('ctrl_l')
            self.current_keys.add('alt_l')

        # Safe Exit: Ctrl + Alt + 0
        if all(k in self.current_keys for k in ['ctrl_l', 'alt_l', '0']):
            print("\n[!] Safe Exit triggered. Cleaning up...")
            if self.tray and self.tray.icon:
                self.tray.icon.stop()
            self.stop_app()

        if not self.recording:
            for profile in self.config['profiles']:
                if all(kn in self.current_keys for kn in profile['key_names']):
                    self.active_profile = profile
                    self.start_recording()
                    break

    def on_release(self, key):
        name = self._get_key_name(key)
        if name in self.current_keys:
            self.current_keys.remove(name)
        
        if name == 'alt_gr':
            if 'ctrl_l' in self.current_keys: self.current_keys.remove('ctrl_l')
            if 'alt_l' in self.current_keys: self.current_keys.remove('alt_l')
        
        if self.recording and self.active_profile:
            if name in self.active_profile['key_names']:
                audio = self.stop_recording()
                if audio is not None:
                    threading.Thread(target=self.process_and_action, args=(audio,)).start()
                else:
                    self.active_profile = None

    def process_and_action(self, audio):
        raw_text = self.transcribe_audio(audio)
        if raw_text:
            print(f" \"{raw_text}\" -> ", end="", flush=True)
            refined_text = self.refine_text(raw_text)
            print(f"Done.")
            self.perform_action(refined_text, raw_text)
            
        time.sleep(1.0)
        self.indicator.hide()
        self.active_profile = None

if __name__ == "__main__":
    # 1. Initialize UI (Main Thread Owner)
    indicator = RecordingIndicator()
    
    # 2. Initialize App Logic (Pass UI reference)
    app = GroqSTT(indicator)
    
    # 3. Start Background Threads (Listener, Tray)
    app.start()
    
    # 4. Start Blocking UI Loop (Must be last)
    try:
        indicator.start_loop()
    except KeyboardInterrupt:
        print("\nExiting...")
        os._exit(0)