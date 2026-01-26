import json
import os

LOG_FILE = "history.log"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def view_history():
    if not os.path.exists(LOG_FILE):
        print("\n[!] No history log found yet.")
        return

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if not lines:
            print("\n[!] History log is empty.")
            return

        clear_screen()
        print("="*60)
        print(f"   📜 HANDY-GROQ HISTORY ({len(lines)} entries)")
        print("="*60)
        
        # Show last 10 entries by default, reverse order
        for i, line in enumerate(reversed(lines)):
            if i >= 10: break
            try:
                entry = json.loads(line)
                print(f"\n[{entry['timestamp']}] ({entry['profile']})")
                print(f"Input:  {entry.get('raw_text', '')}")
                print(f"Output: {entry.get('refined_text', '')}")
                print("-" * 60)
            except json.JSONDecodeError:
                # Handle lagacy plain text logs if any
                print(f"\n[RAW]: {line.strip()}")
                print("-" * 60)
        
        print("\n(Showing last 10 entries)")
            
    except Exception as e:
        print(f"\n[ERROR] Could not read history: {e}")

if __name__ == "__main__":
    view_history()
