import json
import os
import time

CONFIG_PATH = "config.json"

STT_MODELS = [
    "whisper-large-v3-turbo",
    "whisper-large-v3"
]

AI_MODELS = [
    "groq/compound",
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "moonshotai/kimi-k2-instruct",
    "openai/gpt-oss-120b",
    "qwen/qwen3-32b"
]

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def settings_menu():
    while True:
        config = load_config()
        clear_screen()
        print("="*55)
        print("         ⚙️  HANDY-GROQ SETTINGS MANAGER")
        print("="*55)
        print(f" 1. STT Model          : {config['stt_model']}")
        print(f" 2. Refinement Model   : {config['refinement_model']}")
        print(f" 3. Refinement Enabled : {'✅ Yes' if config['refinement_enabled'] else '❌ No'}")
        print(f" 4. Play Sounds        : {'✅ Yes' if config.get('play_sounds', True) else '❌ No'}")
        print(f" 5. Action Mode        : {config.get('action_mode', 'type').upper()}")
        print(f" 6. Log History        : {'✅ Yes' if config.get('log_history', True) else '❌ No'}")
        print(" 7. Edit Profiles (Hotkeys/Prompts)")
        print(" 0. Back to Main Menu")
        print("-" * 55)
        
        choice = input("Select an option (0-7): ")
        
        if choice == "1":
            clear_screen()
            print("--- Select STT Model ---")
            for i, m in enumerate(STT_MODELS):
                print(f" {i+1}. {m}")
            sub_choice = input(f"\nChoose (1-{len(STT_MODELS)}) or Enter to keep: ")
            if sub_choice.isdigit() and 1 <= int(sub_choice) <= len(STT_MODELS):
                config['stt_model'] = STT_MODELS[int(sub_choice)-1]

        elif choice == "2":
            clear_screen()
            print("--- Select AI Refinement Model ---")
            for i, m in enumerate(AI_MODELS):
                print(f" {i+1}. {m}")
            sub_choice = input(f"\nChoose (1-{len(AI_MODELS)}) or Enter to keep: ")
            if sub_choice.isdigit() and 1 <= int(sub_choice) <= len(AI_MODELS):
                config['refinement_model'] = AI_MODELS[int(sub_choice)-1]

        elif choice == "3":
            config['refinement_enabled'] = not config['refinement_enabled']
        elif choice == "4":
            config['play_sounds'] = not config.get('play_sounds', True)
        elif choice == "5":
            clear_screen()
            modes = ['type', 'copy', 'type_and_copy']
            print("--- Select Action Mode ---")
            for i, m in enumerate(modes):
                print(f" {i+1}. {m}")
            sub_choice = input(f"\nChoose (1-3) or Enter to keep: ")
            if sub_choice.isdigit() and 1 <= int(sub_choice) <= 3:
                config['action_mode'] = modes[int(sub_choice)-1]
        elif choice == "6":
            config['log_history'] = not config.get('log_history', True)
        elif choice == "7":
            edit_profiles(config)
            continue
        elif choice == "0":
            break
        else:
            continue
            
        save_config(config)
        print("\nSaving changes...")
        time.sleep(0.5)

def edit_profiles(config):
    while True:
        clear_screen()
        print("="*55)
        print("   📂 EDIT PROFILES")
        print("="*55)
        for i, p in enumerate(config['profiles']):
            print(f" {i+1}. {p['name']} ({' + '.join(p['hotkey'])})")
        print(" 0. Back")
        print("-" * 55)
        
        choice = input("Select profile to edit: ")
        if choice == "0": break
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(config['profiles']):
                p = config['profiles'][idx]
                clear_screen()
                print(f"Editing Profile: {p['name']}")
                print("-" * 30)
                print(f"Current Hotkey: {' '.join(p['hotkey'])}")
                print("Tip: Use 'grave' for the ~ key, 'alt_l' for left Alt.")
                new_hk = input("Enter new hotkeys (e.g., alt_l grave) or Enter to keep: ")
                if new_hk: p['hotkey'] = new_hk.split()
                
                print(f"\nCurrent Prompt: {p['prompt']}")
                new_prompt = input("Enter new prompt or Enter to keep: ")
                if new_prompt: p['prompt'] = new_prompt
                
                save_config(config)
                print("\nProfile updated!")
                time.sleep(1)
        except ValueError:
            pass

if __name__ == "__main__":
    settings_menu()
