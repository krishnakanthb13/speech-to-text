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
try:
    import ctypes
    try:  # Windows 8.1+
        # PROCESS_PER_MONITOR_DPI_AWARE = 2
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except AttributeError:  # Windows Vista/7
        ctypes.windll.user32.SetProcessDPIAware()
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

# Load environment variables
load_dotenv()

class RecordingIndicator:
    def __init__(self):
        self.root = None
        self.status_dot = None
        self.label = None
        self.visible = False
        self.state = "idle"
        self.animation_id = None
        self.dot_pulse = 0
        if not TK_AVAILABLE:
            print("[INFO] Tkinter not found. Visual indicator disabled.")

    def show(self, text="Listening...", state="recording"):
        if not TK_AVAILABLE: return
        if not self.root: self._create_window()
        self._update_state(state)
        self.root.deiconify()
        self.visible = True
        self._pulse()

    def _update_state(self, state):
        """Centralized state update for UI elements."""
        self.state = state
        if not self.canvas: return
        
        # Colors: Red (Recording), Yellow (Processing), Green (Completed)
        states = {
            "recording": ("Listening...", "#ff4444"),    # Red
            "processing": ("Processing...", "#ffbb00"),  # Yellow
            "typing": ("Done", "#00cc00")                # Green
        }
        text, color = states.get(state, ("...", "white"))
        
        self.canvas.itemconfig(self.text_id, text=text, fill=color)
        self.canvas.itemconfig(self.box_id, outline=color)

        # Handle "Done" Checkmark visibility
        # Position checkmark where the dot usually is (or slightly adjusted)
        if state == "typing":
            self.canvas.itemconfig(self.check_line1, state='normal', fill=color)
            self.canvas.itemconfig(self.check_line2, state='normal', fill=color)
            # Center "Done" text? It is already centered.
        else:
            self.canvas.itemconfig(self.check_line1, state='hidden')
            self.canvas.itemconfig(self.check_line2, state='hidden')

        # Stop pulse animation if not recording
        if state != "recording":
             self.canvas.itemconfig(self.dot_id, fill=color)
        
        # Hide dot during "Done" (replaced by checkmark)
        if state == "typing":
            self.canvas.itemconfig(self.dot_id, state='hidden')
        else:
            self.canvas.itemconfig(self.dot_id, state='normal')

    def hide(self):
        if not TK_AVAILABLE: return
        self.state = "idle"
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        if self.root: self.root.withdraw()
        self.visible = False

    def _create_window(self):
        global TK_AVAILABLE
        if not TK_AVAILABLE: return
        try:
            self.root = tk.Tk()
            self.root.overrideredirect(True)
            self.root.attributes("-topmost", True)
            self.root.attributes("-alpha", 0.90)
            
            # Transparent background key
            bg_color = "#1e1e1e" # Dark background
            transparent_key = "#000001"
            
            self.root.configure(bg=transparent_key)
            self.root.attributes("-transparentcolor", transparent_key)
            
            # Size and position
            width, height = 160, 40 
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width // 2) - (width // 2)
            y = screen_height - 120
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            
            # Canvas
            self.canvas = tk.Canvas(self.root, width=width, height=height, bg=transparent_key, highlightthickness=0)
            self.canvas.pack()
            
            # 1. Basic Box (Rectangle) - Clean sharp edges
            # Inset by 2px to ensure 2px border doesn't get clipped
            self.box_id = self.canvas.create_rectangle(
                2, 2, width-2, height-2,
                fill=bg_color,
                outline="white",
                width=2
            )
            
            # 2. Text Label - Centered
            self.text_id = self.canvas.create_text(
                width//2 - 10, height//2, # Slightly left of center to balance the dot on right
                text="Listening...",
                fill="white",
                font=("Segoe UI", 10, "bold")
            )

            # 3. Status Dot - To the RIGHT of text
            # Width 160. Center 80. Text ends approx 115.
            # Put dot at 135
            self.dot_id = self.canvas.create_oval(
                130, height//2 - 4, 
                138, height//2 + 4, 
                fill="white", outline=""
            )
            
            # 4. Vector Checkmark - Same position as dot (Right side)
            cx, cy = 134, height//2 
            self.check_line1 = self.canvas.create_line(
                cx-5, cy+1, cx-1, cy+5, 
                fill="#00cc00", width=2, capstyle=tk.ROUND, state='hidden'
            )
            self.check_line2 = self.canvas.create_line(
                cx-1, cy+5, cx+6, cy-4, 
                fill="#00cc00", width=2, capstyle=tk.ROUND, state='hidden'
            )

        except Exception as e:
            print(f"[WARN] UI Init Failed: {e}")
            TK_AVAILABLE = False

    def _pulse(self):
        if not self.visible or self.state != "recording": return
        self.dot_pulse = (self.dot_pulse + 1) % 2
        
        # Pulse the dot opacity or color
        # Since we use the border/text for main color, let's just pulse the dot between red and white
        # But wait, _update_state sets the color.
        # Let's pulse the Dot for "Recording" specifically.
        
        base_color = "#ff4444" # Red
        # Toggle between base color and a lighter/white shade
        pulse_color = "white" if self.dot_pulse == 0 else base_color
        
        if self.canvas and self.dot_id:
             self.canvas.itemconfig(self.dot_id, fill=pulse_color)
             
        self.animation_id = self.root.after(500, self._pulse)

    def update_text(self, text, state=None):
        if not TK_AVAILABLE: return
        if state:
            self._update_state(state)

    def start_loop(self):
        if not TK_AVAILABLE: return
        self._create_window()
        if self.root:
            self.root.withdraw()
            self.root.mainloop()

class GroqSTT:
    def __init__(self):
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
        
        # UI Indicator
        self.indicator = RecordingIndicator()
        self.ui_thread = threading.Thread(target=self.indicator.start_loop, daemon=True)
        self.ui_thread.start()
        
        self.check_microphone()
        self.current_keys = set()
        self.active_profile = None
        
        self._print_banner()

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
            pass  # Sound is not critical

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
        except Exception as e:
            print(f" Transcription fail: {e}"); self.play_sound("error"); return None
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
        except Exception as e:
            print(f" Refinement fail: {e}"); return text

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
            with open("history.log", "a", encoding="utf-8") as f:
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
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e: print(f"Logging error: {e}")

    def _get_key_name(self, key):
        """Unified key naming for both special keys and character keys."""
        try:
            if hasattr(key, 'name') and key.name:
                name = key.name
                # Normalize common modifier names
                if name == 'ctrl': return 'ctrl_l'
                if name == 'alt': return 'alt_l'
                if name == 'shift': return 'shift_l'
                return name
            if hasattr(key, 'char') and key.char:
                return key.char.lower()
            
            # Fallback for weird cases (like Numpad or AltGr combinations)
            s = str(key).lower().strip("'").strip('"')
            if 'key.' in s:
                s = s.replace('key.', '').strip()
            
            # Map Numpad virtual key codes to numbers
            numpad_map = {
                '<96>': '0', '<97>': '1', '<98>': '2', '<99>': '3',
                '<100>': '4', '<101>': '5', '<102>': '6', '<103>': '7',
                '<104>': '8', '<105>': '9'
            }
            return numpad_map.get(s, s)
        except Exception:
            return str(key).lower()

    def on_press(self, key):
        name = self._get_key_name(key)
        self.current_keys.add(name)
        
        # Windows AltGr handling: AltGr = Ctrl + Alt
        if name == 'alt_gr':
            self.current_keys.add('ctrl_l')
            self.current_keys.add('alt_l')

        # Safe Exit: Ctrl + Alt + 0
        if all(k in self.current_keys for k in ['ctrl_l', 'alt_l', '0']):
            print("\n[!] Safe Exit triggered. Cleaning up...")
            self.indicator.hide()
            if self.recording:
                self.stop_recording()
            sys.exit(0)

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
            # If ANY key from the active combo is released, stop recording
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
            
            # Atomic Action: Only modify clipboard/type once with the final result
            self.perform_action(refined_text, raw_text)
            
        time.sleep(1.0) # Show success state for a moment
        self.indicator.hide()
        self.active_profile = None

    def run(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

if __name__ == "__main__":
    app = GroqSTT()
    try: app.run()
    except KeyboardInterrupt: print("\nExiting...")
