#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "==> Installing frontend dependencies"
(cd frontend && npm install)

echo "==> Installing backend dependencies"
(cd backend && pip install -r requirements.txt)

echo "==> Downloading model weights (one-time, needs internet)"
python models/download_models.py

echo ""
echo "Setup complete. Run:"
echo "  npm install          # root Tauri CLI"
echo "  npm run tauri:dev      # dev mode"
echo "  npm run tauri:build    # build .app"
