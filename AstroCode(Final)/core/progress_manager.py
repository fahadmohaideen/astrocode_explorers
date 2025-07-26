import json
import os

SAVE_FILE = "save_data.json"


def save_progress(highest_level_unlocked):
    """Saves the player's highest unlocked level to a file."""
    data = {"highest_level_unlocked": highest_level_unlocked}
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)
        print(f"Progress saved. Highest level unlocked: {highest_level_unlocked}")
    except Exception as e:
        print(f"Error saving progress: {e}")


def load_progress():
    """Loads the player's progress. If no save file, defaults to level 1."""
    # Default progress for a new player
    default_progress = 1

    if not os.path.exists(SAVE_FILE):
        print("No save file found. Starting new game.")
        return default_progress

    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
            progress = data.get("highest_level_unlocked", default_progress)
            print(f"Progress loaded. Highest level unlocked: {progress}")
            return progress
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error loading or parsing save file: {e}. Resetting to default.")
        return default_progress