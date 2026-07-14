import os
import json
import shutil

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

REQUIRED_CONFIG_KEYS = {"stt_model", "refinement_model", "refinement_enabled", "profiles"}

REQUIRED_PROFILE_KEYS = {"hotkey", "name", "prompt"}


def load_config():
    """Load config.json with JSONDecodeError recovery via .bak fallback."""
    config_path = CONFIG_PATH
    bak_path = config_path + ".bak"

    for path in (config_path, bak_path):
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
            if path == bak_path:
                # Restore the good backup as the primary file
                shutil.copy2(bak_path, config_path)
            return config
        except json.JSONDecodeError:
            continue

    return {}


def save_config(config):
    """Atomically write config.json with backup."""
    bak_path = CONFIG_PATH + ".bak"

    # Keep a backup of the current file before overwriting
    if os.path.exists(CONFIG_PATH):
        shutil.copy2(CONFIG_PATH, bak_path)

    tmp_path = CONFIG_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, CONFIG_PATH)


def validate_config(config):
    """Validate config structure. Returns (ok, list_of_errors)."""
    errors = []

    if not isinstance(config, dict):
        return False, ["Config is not a JSON object"]

    for key in REQUIRED_CONFIG_KEYS:
        if key not in config:
            errors.append(f"Missing required key: {key}")

    if "profiles" in config:
        if not isinstance(config["profiles"], list) or len(config["profiles"]) == 0:
            errors.append("profiles must be a non-empty list")
        else:
            seen_names = set()
            for i, profile in enumerate(config["profiles"]):
                for key in REQUIRED_PROFILE_KEYS:
                    if key not in profile:
                        errors.append(f"Profile {i} missing '{key}'")

                name = profile.get("name", "")
                if name in seen_names:
                    errors.append(f"Duplicate profile name: {name}")
                seen_names.add(name)

    if "stt_model" in config and not isinstance(config["stt_model"], str):
        errors.append("stt_model must be a string")

    if "refinement_enabled" in config and not isinstance(config["refinement_enabled"], bool):
        errors.append("refinement_enabled must be a boolean")

    if "rate_limit_retries" in config:
        if not isinstance(config["rate_limit_retries"], int) or config["rate_limit_retries"] < 0:
            errors.append("rate_limit_retries must be a non-negative integer")

    if "rate_limit_wait_seconds" in config:
        if not isinstance(config["rate_limit_wait_seconds"], (int, float)) or config["rate_limit_wait_seconds"] < 0:
            errors.append("rate_limit_wait_seconds must be a non-negative number")

    return len(errors) == 0, errors
