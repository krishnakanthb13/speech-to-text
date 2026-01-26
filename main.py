import os
import time
import queue
import threading
import wave
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
    try: # Windows 8.1+
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except: # Windows Vista/7
        ctypes.windll.user32.SetProcessDPIAware()
except: pass

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
        self.canvas = None
        self.text_id = None
        self.visible = False
        self.state = "idle"
        self.animation_counter = 0
        if not TK_AVAILABLE:
            print("[INFO] Tkinter not found. Visual indicator disabled.")

    def show(self, text="🎧 Listening", state="recording"):
        if not TK_AVAILABLE: return
        self.state = state
        if not self.root: self._create_window()
        
        # Update text/icon based on state
        display_text = text
        if state == "recording": display_text = "🎧 Listening"
        elif state == "processing": display_text = "🤖 Processing"
        elif state == "typing": display_text = "📑 Finished"
        
        self.canvas.itemconfig(self.text_id, text=display_text)
        self.root.deiconify()
        self.visible = True
        self._animate()

    def hide(self):
        if not TK_AVAILABLE: return
        self.state = "idle"
        if self.root: self.root.withdraw()
        self.visible = False

    def _create_window(self):
        global TK_AVAILABLE
        if not TK_AVAILABLE: return
        try:
            self.root = tk.Tk()
            self.root.overrideredirect(True)
            self.root.attributes("-topmost", True)
            self.root.attributes("-alpha", 0.95)
            self.root.attributes("-toolwindow", True)
            
            # Make the window background transparent
            transparent_color = "#000001"
            self.root.configure(bg=transparent_color)
            self.root.attributes("-transparentcolor", transparent_color)
            
            # Compact Pill Size
            width, height = 220, 50
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width // 2) - (width // 2)
            y = screen_height - 100
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            
            # Canvas for drawing the pill
            self.canvas = tk.Canvas(self.root, width=width, height=height, bg=transparent_color, highlightthickness=0)
            self.canvas.pack()
            
            # Draw Pill Shape (Rounded Rectangle)
            self._draw_pill(0, 0, width, height, radius=25, color="#1e1e1e")
            
            # Text Element
            self.text_id = self.canvas.create_text(
                width//2 + 10, height//2, 
                text="🎧 Listening", 
                fill="white", 
                font=("Segoe UI", 12, "bold")
            )

        except Exception as e:
            print(f"[WARN] UI Init Failed: {e}")
            TK_AVAILABLE = False

    def _draw_pill(self, x1, y1, x2, y2, radius, color):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return self.canvas.create_polygon(points, smooth=True, fill=color, outline="#333333", width=1)

    def _animate(self):
        if not self.visible or self.state == "idle": return
        self.animation_counter += 1
        self.canvas.delete("anim") # Clear previous animation frame
        
        cx, cy = 25, 25 # Icon/Anim position (Left side)
        
        if self.state == "recording":
            # Red Pulse
            pulse = (math.sin(self.animation_counter * 0.2) + 1) * 3
            self.canvas.create_oval(cx-4-pulse, cy-4-pulse, cx+4+pulse, cy+4+pulse, outline="#ff4b2b", width=2, tags="anim")
            self.canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="#ff4b2b", outline="", tags="anim")
            
        elif self.state == "processing":
            # Orange Spinner
            angle = (self.animation_counter * 0.3) % (2 * math.pi)
            r = 8
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#444", width=2, tags="anim")
            sx = cx + r * math.cos(angle)
            sy = cy + r * math.sin(angle)
            self.canvas.create_oval(sx-3, sy-3, sx+3, sy+3, fill="#ffa500", outline="", tags="anim")

        elif self.state == "typing":
            # Green Check
            self.canvas.create_text(cx, cy, text="✓", fill="#4caf50", font=("Arial", 16, "bold"), tags="anim")

        self.root.after(40, self._animate)

    def update_text(self, text, state=None):
        if not TK_AVAILABLE: return
        # Map old text calls to new state logic if needed, or just use state
        if state: self.state = state
        
        display_text = text
        if self.state == "recording": display_text = "🎧 Listening"
        elif self.state == "processing": display_text = "🤖 Processing"
        elif self.state == "typing": display_text = "📑 Finished"
        
        if self.canvas and self.text_id:
            self.canvas.itemconfig(self.text_id, text=display_text)

    def start_loop(self):
        if not TK_AVAILABLE:
            return
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
        except: pass

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
        if mode in ["copy", "type_and_copy"]: pyperclip.copy(text)
        if mode in ["type", "type_and_copy"]:
            self.indicator.update_text("TYPING...", "typing")
            # Safety delay to ensure physically held keys are released by the OS
            time.sleep(0.2)
            self.keyboard_controller.type(text)
        
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
        except:
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
            os._exit(0)

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
