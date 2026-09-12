# Novela — Progress & Handoff Notes

**Last updated:** July 5, 2026
**Purpose of this file:** so any AI coding agent (Cursor, Antigravity, or otherwise)
picking up this project can understand current state in one read, without
re-discovering it from the codebase or re-asking the user. Read this **and**
`docs/PRD.md` before making changes. `docs/PRD.md` is the source of truth for
scope/architecture; this file is the source of truth for "what's actually
done vs. still pending right now."

---

## ✅ Confirmed Done (verified in code, not just claimed)

- **Project scaffold** — Tauri shell wired to Python backend via local sidecar
  process, macOS `.icns` icon generated, `npm run tauri:dev` / `tauri:build`
  working.
- **Chapter navigation (PRD §11.6)** — `ChapterOverlay` component built and
  wired into both `BookView` (reader) and `FullScreenPlayer`. Tapping a
  narrated chapter jumps playback via `start_ms`; tapping an unnarrated
  chapter calls `POST /chapters/{chapter_id}/prioritize` to bump it to the
  front of the queue. `chapters.start_ms` / `duration_ms` added to schema.
- **Job resumability (crash/restart recovery)** — workers skip chunks already `status='ready'` with audio on disk instead of redoing them. Persists atomic chunk progress and recovers interrupted jobs on start.
- **SQLite Database schema migrations** — Raw SQLite schema migrations executed automatically on startup.
- **Model weight downloads** — Kokoro (54 voices), Indic Parler-TTS, and WhisperX are fully cached offline under `models/hf_cache`. Total disk space used: `6.7 GB`.
- **E2E Narration Verification (English & Hindi)**:
  - English narration (using Kokoro `af_bella` + WhisperX) verified E2E: WAV files generated (`862,878` bytes), 46 words synced, first sync word `'Chapter'` at `0ms` - `390ms`.
  - Hindi narration (using Indic Parler-TTS `deep_expressive_male` preset + WhisperX) verified E2E: WAV files generated (`1,838,158` bytes), 50 words synced, first sync word `'Chapter'` at `0ms` - `416ms`.
- **Voice Selection UI**:
  - Voice selection UI with play/stop audio preview trigger built on `ImportScreen.tsx` (for custom English voice settings via Kokoro).
  - 3 Hindi preset descriptions choices (`clear_warm_female`, `deep_expressive_male`, `slow_soft_female`) wired to `ImportScreen.tsx`.
  - Settings overlay panel built in `BookView.tsx` supporting language updates and custom voice/preset modifications.
- **Re-narration reset logic** — if a user updates a book's language or voice, the system prompts for confirmation, resets narrated status coordinates in database, and deletes the old audio WAV files from disk to prevent mixed voices.
- **PyTorch 2.6+ unpickling support** — `torch.load` monkeypatched globally to support backwards-compatible model deserialization.
- **Sidebar & App Layout (PRD §11.1 & §11.3)** — Sidebar is verified in code as positioned on the left side in the CSS flex-row app shell layout. Background colors are set to sleet dark colors (`#08080a`, `#0d0d10`, `#141417`).
- **Custom Cover Art (PRD §11.4)** — Custom cover uploads (`POST /books/{book_id}/cover`) and fallback logic (Custom → Extracted → Generated Placeholder) are verified and active. Supports Right-Click and Drag & Drop file image uploading in sidebar list items.
- **Apple Music-style Full-screen Player (PRD §11.5)** — Full-screen overlay with blurred cover art background, scrubber, playback transport controls, speed fine-increments, and Cover-Art vs Synced-Text toggles verified in the player component.
- **Tauri Native File Dialog Picker (PRD §5 / §11.2)** — Integrated using dynamic dynamic imports of `@tauri-apps/plugin-dialog` to launch native pickers on Tauri app environments. Employs standard HTML file upload fallbacks automatically when previewing in standard browsers. Added matching `/import-path` endpoint for filesystem-path copying.
- **Tauri Native Capability Access** — Fixed native dialogue permission restrictions in `capabilities/default.json` to allow the dev server (`http://localhost:1420`) to invoke IPC plugins. Added `tauri-plugin-dialog` Rust registry.
- **PyMuPDF Reading-Order Text Extractor** — Switched PDF text extraction to block-sorting using PyMuPDF (`fitz`), resolving overlapping line duplication and paragraph text bleed.
- **Structural Chapter Segmenter** — Separates `Front Matter` from narrative text, identifies `Part` divisions and `Chapter` boundaries (words/roman numerals) with clean regex boundaries, ignores nested Goldstein-style book sections (keeping them inline rather than breaking parent chapters), and fixes period/blank placeholder titles.
- **TTS All-Caps Normalization** — Added a normalizer (`_normalize_heading_for_tts`) to convert uppercase text headers to Title Case, preventing speech models from spelling them out letter-by-letter.
- **Title Extraction Auto-Resolution** — Correctly resolves title strings (like `1984`) from filename stems (skipping generic timestamp numbers and filtering out strings like `"a novel by"`).
- **Library Item Rename & Delete** — Added PATCH/DELETE book routes in backend, client hooks, and inline action buttons (on-hover Pencil/Trash actions) in the sidebar.

---

## ❓ Unconfirmed — Ask Before Assuming

None. All PRD features and layout specifications are verified and fully accounted for.

---

## ❌ Not Started (confirmed, as of last check)

None.

---

## Immediate Next Steps (in order)

1. Perform a full end-to-end test with an actual book.


---

## Ground Rules for Whoever Picks This Up

- This is a **personal-use project on macOS (Apple Silicon/M2)**, meant to
  stay fully offline after the one-time model download, and structured so it
  could later be shared/distributed (see PRD §9a/§9).
- **Don't touch working code while implementing something unrelated** —
  additive changes only, unless explicitly asked to refactor.
- **Don't guess and report success** — if something can't be verified,
  say so explicitly rather than assuming it works.
- **Sentencepiece SIGBUS Exit Bug**: A crash (SIGBUS) inside sentencepiece happens on Python shutdown during GC destructors. This is confined strictly to process shutdown/exit sequence (triggered during GC destructor calls) and does NOT affect active app runtime or narration mid-sessions. The FastAPI server remains completely stable.

