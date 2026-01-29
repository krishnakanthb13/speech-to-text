import os
import json
import shutil
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from groq import Groq
from dotenv import load_dotenv

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.json")
HISTORY_PATH = os.path.join(PROJECT_ROOT, "history.log")
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")

# Load environment
load_dotenv(ENV_PATH)

app = Flask(__name__)
CORS(app)

# Initialize Flask-Limiter with file-based storage
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["15 per minute"],
    storage_uri="memory://"  # Use memory storage (resets on restart) - change to "redis://" or "memcached://" for production
)

# Initialize Groq
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("WARNING: GROQ_API_KEY not found.")
client = Groq(api_key=api_key)

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def append_history(entry):
    # Matches the logging format of main.py
    # RotatingFileHandler in main.py writes plain messages, usually with a newline if configured standardly.
    # We will just append to the file.
    try:
        with open(HISTORY_PATH, "a", encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"Error writing history: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'POST':
        new_config = request.json
        save_config(new_config)
        return jsonify({"status": "success", "config": new_config})
    return jsonify(load_config())

@app.route('/api/history', methods=['GET'])
def get_history():
    history = []
    if not os.path.exists(HISTORY_PATH):
        return jsonify([])

    try:
        # Efficiently read the last 50 lines by seeking from the end
        with open(HISTORY_PATH, "rb") as f:
            f.seek(0, os.SEEK_END)
            pos = f.tell()
            buffer = b""
            lines = []
            
            # Read backwards in 4KB chunks until we have enough lines
            while pos > 0 and len(lines) <= 50:
                chunk_size = min(pos, 4096)
                pos -= chunk_size
                f.seek(pos)
                chunk = f.read(chunk_size)
                buffer = chunk + buffer
                lines = buffer.splitlines()
            
            # Process the last 50 lines (newest first)
            for line_bytes in reversed(lines[-50:]):
                line = line_bytes.decode('utf-8', errors='ignore').strip()
                if line:
                    try:
                        history.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
                        
        return jsonify(history)
    except Exception as e:
        print(f"Error reading history: {e}")
        return jsonify([])

@app.route('/api/record', methods=['POST'])
@limiter.limit("15 per minute")
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file"}), 400
    
    audio_file = request.files['audio']
    profile_name = request.form.get('profile', 'General')
    
    # Save temp
    temp_filename = os.path.join(BASE_DIR, "temp_upload.webm") # Browser usually sends webm
    audio_file.save(temp_filename)
    
    config = load_config()
    file_path_to_send = temp_filename
    
    # 1. Transcribe
    try:
        with open(file_path_to_send, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(temp_filename, file.read()),
                model=config.get('stt_model', 'whisper-large-v3')
            )
        raw_text = transcription.text.strip()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    # 2. Refine
    refined_text = raw_text
    profile = next((p for p in config['profiles'] if p['name'] == profile_name), None)
    
    if config.get('refinement_enabled', True):
        prompt = profile['prompt'] if profile else "Clean up this text."
        
        # Parse Chat Params
        chat_params_json = request.form.get('chatParams')
        if chat_params_json:
            try:
                params = json.loads(chat_params_json)
                
                # Validate chat params - must be integers between 0 and 100
                valid_keys = ['humanRobot', 'factCreative', 'funnyRage', 'expertLame', 'formalSlang']
                for key, value in params.items():
                    if key not in valid_keys:
                        return jsonify({"error": f"Invalid parameter: {key}"}), 400
                    if not isinstance(value, (int, float)) or not (0 <= value <= 100):
                        return jsonify({"error": f"Invalid value for {key}: must be between 0 and 100"}), 400
                
                # Dynamic Prompt Injection (AGGRESSIVE MODE)
                extras = []
                
                # Human <-> Robot
                hr = params.get('humanRobot', 50)
                if hr < 40: extras.append("STYLE: You are an emotional human. Use hesitation, feelings, and warmth. Rewrite the text to sound purely human.")
                elif hr > 60: extras.append("STYLE: You are a ROBOT. Use efficient, cold, calculated logic. NO emotion. Output should be like a log file or code comment.")
                
                # Fact <-> Creative
                fc = params.get('factCreative', 50)
                if fc < 40: extras.append("CONTENT: Be brutally factual. Remove any fluff. concise.")
                elif fc > 60: extras.append("CONTENT: Be highly CREATIVE. Embellish the details. Paint a vivid picture. Use metaphors.")
                
                # Funny <-> Rage
                fr = params.get('funnyRage', 50)
                if fr < 40: extras.append("TONE: You are a Stand-up Comedian. Make it funny. Insert jokes/puns related to the text.")
                elif fr > 60: extras.append("TONE: You are ANGRY. The text makes you mad. Rant about it. Use uppercase for checking/emphasis!")
                
                # Expert <-> Lame
                el = params.get('expertLame', 50)
                if el < 40: extras.append("COMPLEXITY: PhD Level. Use jargon, technical complexity, and sophisticated vocabulary.")
                elif el > 60: extras.append("COMPLEXITY: Explain Like I'm 5 (ELI5). Use simple words. dumb it down.")
                
                # Formal <-> Slang
                fs = params.get('formalSlang', 50)
                if fs < 40: extras.append("LANGUAGE: Victorian Formal. 'Thou', 'Shall', extremely polite and structured.")
                elif fs > 60: extras.append("LANGUAGE: Gen-Z / Street Slang. Use 'bruh', 'no cap', 'fr', emojis. Make it trendy.")
                
                if extras:
                    # Override base prompt to ensure specific instructions are followed
                    prompt = "TASK: Rewrite the following transcript completely based on these identity rules:\n"
                    prompt += "\n".join(extras)
                    prompt += "\n\nCRITICAL: Do not just fix grammar. You MUST assume the persona described above. Change words, sentence structure, and tone to match."
                    
                print(f"DEBUG: Chat Params: {params}")
                print(f"DEBUG: Final Prompt: {prompt}")

            except Exception as e:
                print(f"Error parsing chat params: {e}")

        try:
            completion = client.chat.completions.create(
                model=config.get('refinement_model', 'llama-3.3-70b-versatile'),
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": raw_text}
                ]
            )
            refined_text = completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Refinement failed: {e}")

    # 3. Log
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "profile": profile_name,
        "chat_params": request.form.get('chatParams'), # Log params too
        "raw_text": raw_text,
        "refined_text": refined_text,
        "stt_model": config.get('stt_model'),
        "refinement_model": config.get('refinement_model')
    }
    append_history(log_entry)

    return jsonify({
        "status": "success",
        "raw": raw_text,
        "refined": refined_text,
        "entry": log_entry
    })

@app.route('/api/history/delete', methods=['POST'])
def delete_history_item():
    data = request.json
    timestamp_to_delete = data.get('timestamp')
    
    if not timestamp_to_delete:
        return jsonify({"error": "Missing timestamp"}), 400

    if not os.path.exists(HISTORY_PATH):
        return jsonify({"error": "History file not found"}), 404

    try:
        # Read all lines
        with open(HISTORY_PATH, "r", encoding='utf-8') as f:
            lines = f.readlines()
        
        # Rewrite file excluding the matching item using atomic write
        # We assume one entry per line as enforced by append_history
        deleted = False
        
        # Create temp file in the same directory for atomic rename
        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(HISTORY_PATH))
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                for line in lines:
                    try:
                        entry = json.loads(line)
                        if entry.get("timestamp") == timestamp_to_delete:
                            deleted = True
                            continue # Skip writing this line
                        f.write(line)
                    except json.JSONDecodeError:
                        f.write(line) # Preserve malformed lines just in case
            
            # Atomic replace
            shutil.move(temp_path, HISTORY_PATH)
        except Exception:
            # Clean up temp file if something went wrong
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
        
        if deleted:
            return jsonify({"status": "success"})
        else:
            return jsonify({"error": "Item not found"}), 404
            
    except Exception as e:
        print(f"Error deleting history item: {e}")
        return jsonify({"error": str(e)}), 500

import webbrowser
import threading
from waitress import serve

if __name__ == '__main__':
    def open_browser():
        webbrowser.open_new("http://localhost:8091")

    print("===========================================")
    print("    [+] Starting Production Server...")
    print("    --> Open: http://localhost:8091")
    print("    --> Close: Ctrl + C")
    print("===========================================")

    # Open browser after delay
    threading.Timer(1.5, open_browser).start()
    
    # Use waitress for production-grade WSGI server (removes Flask dev warning)
    serve(app, host='0.0.0.0', port=8091)
