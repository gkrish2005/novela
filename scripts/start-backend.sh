#!/usr/bin/env bash
# Start the Novela Python backend for development without Tauri.
cd "$(dirname "$0")/backend"
exec python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8742 --reload
