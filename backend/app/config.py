"""App configuration and paths."""

from __future__ import annotations

import os
import platform
from pathlib import Path

APP_NAME = "Novela"
BACKEND_PORT = int(os.environ.get("NOVELA_PORT", "8742"))
BACKEND_HOST = os.environ.get("NOVELA_HOST", "127.0.0.1")

REPO_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = REPO_ROOT / "models"
HF_CACHE = MODELS_DIR / "hf_cache"

os.environ.setdefault("HF_HOME", str(HF_CACHE))


def app_data_dir() -> Path:
    if platform.system() == "Darwin":
        base = Path.home() / "Library" / "Application Support" / APP_NAME
    else:
        base = Path.home() / ".local" / "share" / APP_NAME
    base.mkdir(parents=True, exist_ok=True)
    return base


DATA_DIR = app_data_dir()
AUDIO_DIR = DATA_DIR / "audio"
COVERS_DIR = DATA_DIR / "covers"
IMPORTS_DIR = DATA_DIR / "imports"
DB_PATH = DATA_DIR / "novela.sqlite"

for _d in (AUDIO_DIR, COVERS_DIR, IMPORTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)
