"""
docmax-demo Config Manager — single source of truth.

All persistent state lives in ~/.docmax-demo/config.json.
(Previously split between cwd/.docmax-demo.json and ~/.docmax-demo/config.json — now unified.)
"""

from __future__ import annotations

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".docmax-demo"
CONFIG_FILE = CONFIG_DIR / "config.json"


# ---------------------------------------------------------------------------
# Core read / write
# ---------------------------------------------------------------------------

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_config(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=4), encoding="utf-8")


# ---------------------------------------------------------------------------
# Tool paths
# ---------------------------------------------------------------------------

def get_tool_path(tool: str) -> str | None:
    return load_config().get(f"tool_{tool}")


def set_tool_path(tool: str, path: str) -> None:
    config = load_config()
    config[f"tool_{tool}"] = path
    save_config(config)


# ---------------------------------------------------------------------------
# Recent folder  (was in utils.py / cwd — now here)
# ---------------------------------------------------------------------------

def save_recent_folder(folder: str) -> None:
    config = load_config()
    config["recent_folder"] = folder
    save_config(config)


def load_recent_folder() -> str | None:
    return load_config().get("recent_folder")


# ---------------------------------------------------------------------------
# OCR / other user preferences
# ---------------------------------------------------------------------------

def get_preference(key: str, default=None):
    return load_config().get(f"pref_{key}", default)


def set_preference(key: str, value) -> None:
    config = load_config()
    config[f"pref_{key}"] = value
    save_config(config)
