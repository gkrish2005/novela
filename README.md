# Novela

A local-first app that turns PDFs/text into narrated audiobooks with word-level
synced highlighting — in **English or Hindi**. Runs fully offline on Apple
Silicon after a one-time model download.

Full spec: [`docs/PRD.md`](docs/PRD.md) — read this before writing any code.

---

## Stack

- **Frontend/shell:** Tauri (Rust) wrapping a React UI → native macOS `.app`
- **Backend:** Python (PDF parsing, TTS, alignment, ffmpeg) — runs as a local
  sidecar process the Tauri shell talks to over `localhost`
- **TTS:** Kokoro (English), AI4Bharat Indic Parler-TTS (Hindi)
- **Alignment:** WhisperX (word-level timestamps, both languages)
- **Storage:** SQLite (library/metadata) + filesystem (audio files)

## Project Structure

```
/novela
  /frontend        React UI — Tauri wraps this
  /backend         Python: PDF parsing, TTS, alignment, ffmpeg
  /src-tauri       Tauri config, Rust glue, icon, entitlements
  /models          Downloaded TTS + alignment weights (gitignored)
  /docs            PRD and any design notes
  README.md
```

## First-Time Setup

Requirements: Xcode Command Line Tools, Rust (via `rustup`), Node 20+,
Python 3.11+, `ffmpeg` and `espeak-ng` (via Homebrew: `brew install ffmpeg espeak-ng`).

> No Hugging Face account or access token is needed — Kokoro, Indic Parler-TTS,
> and WhisperX are all public, non-gated models that download automatically
> when `models/download_models.py` runs.

```bash
# Quick setup (installs deps + downloads models)
./setup.sh

# Or step by step:
npm install                    # root — Tauri CLI
cd frontend && npm install && cd ..
cd backend && pip install -r requirements.txt && cd ..
python models/download_models.py
```

## Running

```bash
# Full app (Tauri spawns the Python backend automatically)
npm run tauri:dev

# Or run UI + backend separately for debugging:
./scripts/start-backend.sh     # terminal 1
cd frontend && npm run dev     # terminal 2 — open http://localhost:1420
```

## Build the .app

```bash
npm run tauri:build
```

After step 3, everything works offline — see `docs/PRD.md` section 9 for the
full offline-capability breakdown.

## Sharing a Base/Root Version

The git repo itself is the base version. To hand someone a clean zip snapshot:

```bash
git archive --format=zip -o novela-base.zip HEAD -- . ':!models'
```

This excludes `models/` (multi-GB weights — recipients run
`python models/download_models.py` themselves) and relies on `.gitignore`
already keeping personal library data out of the repo.
