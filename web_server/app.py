
import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
import werkzeug

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
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r", encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            # Sometimes logs might have timestamps prefix if formatter changed, 
                            # but main.py uses strictly json.dumps in message.
                            # However, the formatter was '%(message)s', so it should be pure JSON.
                            entry = json.loads(line)
                            history.append(entry)
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            print(f"Error reading history: {e}")
    # Return newest 50 entries
    return jsonify(history[-50:][::-1])

@app.route('/api/record', methods=['POST'])
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
        
        # Rewrite file excluding the matching item
        # We assume one entry per line as enforced by append_history
        deleted = False
        with open(HISTORY_PATH, "w", encoding='utf-8') as f:
            for line in lines:
                try:
                    entry = json.loads(line)
                    if entry.get("timestamp") == timestamp_to_delete:
                        deleted = True
                        continue # Skip writing this line
                    f.write(line)
                except json.JSONDecodeError:
                    f.write(line) # Preserve malformed lines just in case
        
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
    print("    🚀 Starting Production Server...")
    print("    👉 Open: http://localhost:8091")
    print("    👉 Close: Ctrl + C")
    print("===========================================")

    # Open browser after delay
    threading.Timer(1.5, open_browser).start()
    
    # Use waitress for production-grade WSGI server (removes Flask dev warning)
    serve(app, host='0.0.0.0', port=8091)
