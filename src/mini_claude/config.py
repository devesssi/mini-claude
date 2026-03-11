import json
from pathlib import Path

# This saves a hidden file in the user's home folder
CONFIG_FILE = Path.home() / ".mini_claude_config.json"

def save_api_key(api_key):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"GROQ_API_KEY": api_key}, f)

def load_api_key():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get("GROQ_API_KEY")
    return None