"""Save a Kev key in the current user's home folder."""

from pathlib import Path

DEFAULT_KEY_PATH = Path.home() / ".modernism_detector" / "kev_key.txt"


def load_key(path=DEFAULT_KEY_PATH) -> str:
    """Return the saved key, or an empty string when no key is saved."""
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""


def save_key(key, path=DEFAULT_KEY_PATH):
    """Save a trimmed key outside the project folder."""
    key_path = Path(path)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text(key.strip(), encoding="utf-8")


def forget_key(path=DEFAULT_KEY_PATH):
    """Remove a saved key, if one exists."""
    try:
        Path(path).unlink()
    except FileNotFoundError:
        pass
