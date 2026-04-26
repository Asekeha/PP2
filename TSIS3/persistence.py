import json, os

SETTINGS_FILE  = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

DEFAULTS = {
    "sound":      True,
    "car_color":  "cyan",
    "difficulty": "normal",
    "volume":     0.7,
}


def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
            # fill in any missing keys
            for k, v in DEFAULTS.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(DEFAULTS)


def save_settings(cfg: dict) -> None:
    with open(SETTINGS_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def load_leaderboard() -> list:
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE) as f:
                data = json.load(f)
            if isinstance(data, list):
                return sorted(data, key=lambda e: e.get("score", 0), reverse=True)
        except Exception:
            pass
    return []


def save_run(entry: dict) -> None:
    """Add entry and keep top-10 sorted by score."""
    board = load_leaderboard()
    board.append(entry)
    board.sort(key=lambda e: e.get("score", 0), reverse=True)
    board = board[:10]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(board, f, indent=2)
