# Novela — Product Requirements Document (v1.1)

**Status:** Personal project, v1 in progress. Designed to grow into a shareable/launchable app later.
**Target platform:** macOS (Apple Silicon, M2), packaged as a native `.app` via Tauri.
**Owner:** Personal use first, base/root version kept shareable via git.

---

## 1. What This App Does

Novela turns text (books, PDFs, articles) into narrated audio with **word-level
synced highlighting**, like an audiobook that highlights each word as it's spoken —
similar to Kindle's Immersion Reading, but self-hosted and running entirely on your
own machine.

**New in this version:** the app is now bilingual. Every book can be narrated and
captioned in **English or Hindi**, chosen by the user or auto-detected from the
source text.

> **Important constraint:** Novela never translates. It only *detects* which
> language a given passage is already written in (English or Hindi) and narrates/
> displays it in that same language, using the matching voice engine. There is no
> English→Hindi or Hindi→English conversion anywhere in v1.1 — see §3.1 and §12.2.

---

## 2. Supported Input Formats

| Format | Library |
|---|---|
| `.pdf` | `pdfplumber` (text + layout), `PyMuPDF` / `fitz` (fallback + OCR) |
| `.txt` | native |
| `.md` | native |
| `.epub` | `ebooklib` / equivalent |
| `.docx` | `python-docx` |

Pipeline: **book → chapters → chunks → sentences → words**

Text extraction is language-agnostic — Devanagari (Hindi) and Latin (English) text
both flow through the same parser. Language is determined per-book (or per-chapter,
see below) *after* extraction, before TTS generation.

---

## 3. Language Selection (New)

This is the core addition to v1.1.

### 3.1 How language is chosen

1. **Auto-detect on import** — after text extraction, run a lightweight language
   identifier (`fasttext` `lid.176` or `langdetect`) on a text sample per chapter.
   Flag the book as `en`, `hi`, or `mixed` (chapters split by detected language).
2. **User override** — the import screen shows the detected language with a toggle
   (English / Hindi) the user can confirm or change before narration starts.
3. **Per-chapter override** — for books that mix languages (e.g., an English novel
   with Hindi dialogue, or a Hindi book with English chapter titles), the user can
   set language at the chapter level, not just the book level.
4. Whatever language is set determines: which **TTS voice/engine** narrates that
   chunk, and which **alignment model** generates its word timestamps and subtitles.

### 3.2 TTS engines per language

| Language | Engine | Notes |
|---|---|---|
| English | **Kokoro** (existing choice) or Chatterbox | Local inference, already scoped in v1 |
| Hindi | **AI4Bharat Indic Parler-TTS** (default) | Apache-2.0, local inference, native Hindi + English voices, supports prosody/emotion prompting |
| Either (fallback) | **Coqui XTTS-v2** | 17 languages incl. Hindi & English, zero-shot voice cloning, one engine could theoretically cover both if a single-engine setup is preferred later |

Rationale: Kokoro's Hindi voice coverage is thin compared to its English
voicepacks, so Indic Parler-TTS — purpose-built for Indian languages,
Apache-licensed, and trained specifically for Hindi/Indic prosody — is used as
the Hindi default rather than relying on Kokoro's `lang_code='h'` option.
XTTS-v2 is kept as a documented fallback if you'd rather run one multilingual
engine instead of two. **All three models (Kokoro, Indic Parler-TTS, WhisperX)
are public, non-gated Hugging Face models** — no account or access token is
required to download or use any of them.

### 3.3 Alignment (word timestamps) per language

- **WhisperX** (already in the architecture) is kept as the aligner for **both**
  languages — Whisper's multilingual checkpoints handle Hindi ASR well enough for
  forced alignment purposes. The pipeline simply passes `language="hi"` or
  `language="en"` to WhisperX based on the chunk's language tag.
- `aeneas` (your original alt aligner) also supports Hindi via its `espeak`-based
  phonemizer, and remains a valid fallback if WhisperX's Hindi alignment quality
  is ever unsatisfactory for a given book.
- Output format is unchanged: `[{word, start_ms, end_ms, char_offset_start, char_offset_end}]`
  — language does not change the schema, only which model produced it.

### 3.4 Subtitles / captions

- Subtitles are generated from the same word-timestamp data already being produced
  for highlighting — no separate subtitle pipeline needed.
- Subtitle text is stored and rendered in **the same script as the source language**
  (Devanagari for Hindi, Latin for English) — no transliteration or translation is
  performed. This is narration-of-the-original-text, not translation.
- If you later want cross-language subtitles (e.g., Hindi audio with English
  subtitles), that requires a translation step (e.g., `IndicTrans2`) — **out of
  scope for v1.1**, noted here as a possible v2 feature.

---

## 4. Audio Pipeline

- TTS output: `.wav` / `.flac` per chunk
- Post-processing: `ffmpeg-normalize` (loudness normalization), `ffmpeg` for concat
  and encoding to final `.m4b` / `.mp3`
- Playback: HTML `<audio>` element, `playbackRate` for speed control with
  `preservesPitch` enabled so sped-up narration doesn't sound chipmunked
- Sync: `timeupdate` + `requestAnimationFrame` polling `currentTime`, matched
  against each word's `[start_ms, end_ms]` window (`currentTime * 1000`) to drive
  highlighting
- Export: `.m4b` (chaptered audiobook) or `.mp3`

This layer is unaffected by language — it operates on audio and timestamps
regardless of which engine produced them.

---

## 5. System Architecture

```
┌─────────────────────┐
│   Client App (UI)   │  Desktop app (Tauri-wrapped web UI)
│   - Import screen    │  (includes language detect/select control)
│   - Library           │
│   - Reader/Player     │  (renders subtitles in source script)
└─────────┬─────────────┘
          │ local API calls (or IPC if fully native)
┌─────────▼─────────────────────┐
│   App Backend/Core             │
│   - Document parser            │ (PyMuPDF, OCR fallback)
│   - Language detector          │ (fasttext lid.176 / langdetect)   ← new
│   - Chunker/Chapterizer        │
│   - Job queue                  │ (background TTS jobs, resumable)
│   - TTS engine router          │ (Kokoro for en, Indic Parler-TTS   ← updated
│                                 │  for hi, local inference)
│   - Forced aligner              │ (WhisperX, language-aware)         ← updated
│   - Audio post-processor       │ (ffmpeg: concat, normalize, encode .m4b/.mp3)
│   - Local storage layer        │ (SQLite for library/metadata + filesystem for audio)
└─────────────────────────────────┘
```

---

## 6. Data Model (updated)

```sql
books(
  id, title, author, cover_path, source_file_path, created_at,
  total_duration_ms,
  language          -- 'en' | 'hi' | 'mixed'      -- new
)

chapters(
  id, book_id, index, title, audio_path, status,
  language,         -- 'en' | 'hi'                -- new, overrides book default
  start_ms,         -- offset within the book's full-length timeline -- new
  duration_ms       -- chapter length, for the chapter list UI       -- new
)

chunks(
  id, chapter_id, index, text, spoken_text, audio_path, status,
  language,         -- 'en' | 'hi'                -- new
  tts_engine        -- 'kokoro' | 'indic-parler-tts' | 'xtts-v2'   -- new
)

word_timestamps(
  id, chapter_id, word, start_ms, end_ms, char_start, char_end,
  language          -- 'en' | 'hi'                -- new, for subtitle rendering
)

playback_state(book_id, chapter_id, position_ms, speed, updated_at)
```

`language` on `chunks` is what actually drives the TTS engine router per unit of
work — `books.language` and `chapters.language` are display/default conveniences.

---

## 7. macOS Packaging & Icon

- Final build target: `.app`
- Icon: standard `.icns`, generated via `iconutil` or a GUI tool like Image2icon,
  referenced in `tauri.conf.json`'s `icon` field
- Local inference on the M2 should use Metal (`mps` backend in PyTorch) where the
  TTS/alignment libraries support it, for both English and Hindi models
- Code-signing/notarization is **only** needed if/when you distribute the built
  `.app` to others — not required for running it yourself

---

## 8. Project Structure & Dev Workflow

```
/novela
  /frontend        (React/Svelte UI — Tauri wraps this)
  /backend         (Python: PDF parsing, TTS, alignment, ffmpeg)
  /src-tauri       (Tauri config, Rust glue, icon, entitlements)
  models/          (downloaded TTS + alignment weights — gitignored, not committed)
    /kokoro/
    /indic-parler-tts/     ← new
    /whisperx/
  README.md
```

- `git init` from day one, even for personal use — gives you version history and
  makes "change something later" trivial in VS Code, Cursor, or any editor.
- Editing later: this is a normal git repo, so opening `/novela` in VS Code
  (or any editor) and editing frontend/backend code works exactly like any other
  project — nothing here is special-cased to a particular editor.

### Keeping a base/root version to share later

- Treat the **git repository itself** as the base/root version — cleaner than a
  zip because it preserves history and is trivial to update.
- For a literal shareable zip snapshot (e.g., to hand to a friend, or for a future
  release): use `git archive`, or a simple build script, to zip the repo
  **excluding** `models/` (multi-GB weights for *both* language packs now —
  instruct recipients to fetch these via a `setup.sh` / `download_models.py`
  script instead) and excluding any personal library data (books/audio, kept
  outside the repo, e.g. in `~/Library/Application Support/Novela/`).
- Include a `README.md` with setup steps (`npm install`, `pip install -r
  requirements.txt`, `python download_models.py` — now downloading both the
  English and Hindi model sets — `npm run tauri build`) so the zip is genuinely
  runnable by someone else, not just a snapshot of your machine.
- When/if you actually distribute the built `.app` (not just source) to others:
  it will need to be code-signed and notarized via an Apple Developer account for
  Gatekeeper to allow it without a security warning — not required for personal
  use, only relevant at the "launch it as an app" stage later.

---

## 9. Offline Capability — What Works Offline vs What Needs Internet

| Function | Works fully offline? | Notes |
|---|---|---|
| Import PDF/text, extract & chapterize | ✅ Yes | Pure local processing. |
| Detect language (en/hi) | ✅ Yes | `fasttext`/`langdetect` run locally, tiny model, bundled with the app. |
| Generate narration — English (Kokoro) | ✅ Yes | Once weights are downloaded once, all inference runs locally on your M2 — no network calls per book, ever. |
| Generate narration — Hindi (Indic Parler-TTS) | ✅ Yes | Same as above — one-time weight download, then fully local inference. |
| Word-level alignment/timestamps (either language) | ✅ Yes | WhisperX also runs locally once its weights are downloaded once. |
| Subtitle/caption generation | ✅ Yes | Derived from local word-timestamp data, no network involved. |
| Playback + word-sync highlighting | ✅ Yes | All local files, no network needed. |
| Speed control | ✅ Yes | Local audio engine. |
| Export to `.m4b` / `.mp3` | ✅ Yes | Local ffmpeg processing. |
| Sharing the exported file | ✅ Yes (the file itself) | Sending it (AirDrop/email/upload) needs network *at the moment of sending*, but the file itself is fully self-contained and playable offline by whoever receives it. |
| Library browsing, full-screen player | ✅ Yes | All local. |
| **First-time model download** | ❌ Needs internet, once | Downloading Kokoro, Indic Parler-TTS, and WhisperX weights the first time — a few hundred MB to a couple GB per language pack, one-time, then never again unless you choose to update a model. |
| Optional cloud voice / fallback TTS (if added later) | ❌ Needs internet | Only relevant if you explicitly enable an optional cloud model — not part of the default local pipeline. |
| App auto-update check (future, only if distributed) | ❌ Needs internet | Only relevant once/if you ship this to others with an updater; irrelevant for personal use. |

**Bottom line:** after the one-time model downloads during setup (English pack +
Hindi pack), the app is **100% offline-capable** for every core function — import,
detect language, narrate in either language, sync, play, export, share the file,
manage your library. The only things that ever touch the network are (a) the
initial model downloads and (b) anything you deliberately add later, like a cloud
voice option or an auto-updater — neither is required for this to work.

---

## 10. Acceptance Criteria (v1.1 "Done")

- [ ] User can import a PDF or `.txt` file up to ~200,000 words and the app
      extracts clean, chapterized text.
- [ ] App correctly auto-detects whether a book/chapter is English or Hindi, and
      the user can confirm or override this before narration begins.
- [ ] User can select a voice and generate narration in the chosen language; can
      begin listening to Chapter 1 while later chapters still process.
- [ ] Hindi text produces Hindi audio via Indic Parler-TTS; English text produces
      English audio via Kokoro — without the user manually picking an engine.
- [ ] Word-level highlighting stays in sync during playback for both English and
      Hindi narration.
- [ ] Subtitles/captions render correctly in Devanagari for Hindi chunks and Latin
      script for English chunks.
- [ ] A book with mixed-language chapters (e.g. English body, Hindi dialogue)
      narrates each chapter in its own detected/assigned language correctly.
- [ ] Export to `.m4b`/`.mp3` works for books in either language, with correct
      chapter markers.
- [ ] Everything above works with Wi-Fi off, after the one-time model downloads.
- [ ] Project is a git repo openable in VS Code (or any editor); `git archive`
      produces a runnable zip (with `models/` and personal library data excluded)
      that a recipient can set up from the included `README.md`.
- [ ] Library panel is on the **left** side of the window, with the pinned
      mini-player bar at its bottom expanding into full-screen mode when tapped.
- [ ] Import screen and any language toggles make clear the app **detects**
      English/Hindi rather than translating between them.
- [ ] App background uses the darker palette from §11.3; accent/text colors are
      unchanged from the original mockup.
- [ ] User can set a custom cover image per book (right-click/drag-drop), and it
      appears in the library, mini-player, full-screen view, and exported file
      metadata.
- [ ] Full-screen "Now Playing" mode matches §11.5: blurred-art background,
      transport controls, speed control, and a toggle between cover art and the
      synced/highlighted text view with click-to-seek.
- [ ] A chapter list is reachable from both the reader and full-screen player
      (§11.6); tapping any already-narrated chapter jumps playback straight to
      it without stepping through intermediate chapters, and highlight sync
      keeps working immediately after the jump.

---

## 11. UI/UX Specification (New)

This section locks down the visual/interaction details so an AI coding agent
doesn't have to guess. It refines the initial mockup (dark theme, library panel,
import screen) with the following changes.

### 11.1 Layout — Library Panel on the Left

- The library panel moves to the **left** side of the window (the initial mockup
  had it on the right — flip it). Main content (import screen / active reader)
  occupies the remaining space to the right of it.
- Persistent left sidebar, ~280–320px wide (collapsible is a nice-to-have, not
  required for v1.1). Top to bottom:
  1. App title/logo + **"+ New"** import button
  2. Scrollable library list — each row shows cover thumbnail, title,
     language/chapter/progress line (as in the mockup)
  3. A pinned **mini "Now Playing" bar** at the bottom of the sidebar (small
     cover thumbnail, title, current speed) — tapping it expands into the
     full-screen player (§11.5)

### 11.2 Language Behavior — Reflect "Detect, Don't Translate" in the UI

- The import-screen EN/HI toggle is a **detected-language override**, not a
  translation target — rename its tooltip/label if needed so this is unambiguous
  (e.g., "Detected: English — tap to correct" rather than anything implying
  conversion).
- Suggested import-screen copy: *"Novela detects English or Hindi automatically
  and narrates each in its own voice — it doesn't translate."*
- This is a restatement of §3.1/§1 for the UI layer specifically, so the frontend
  copy never implies a translation feature that doesn't exist.

### 11.3 Theme — Slightly Darker Background

- Keep all existing accent/text colors as-is (amber/gold highlight, serif title
  font, warm off-white body text) — only the **base background** gets darker.
- Suggested CSS variable adjustments (fine-tune visually, these are starting
  points, not exact requirements):
  - `--bg-app`: darken to near-black, e.g. `#08080a`
  - `--bg-panel` (sidebar): `#0d0d10`
  - `--bg-card` (library rows, mini-player bar): `#141417`
  - `--accent` (amber) and all text colors: **unchanged**
- Apply consistently across import screen, sidebar, and full-screen player
  background treatment (§11.5 blur layer should also sample from this darker
  palette).

### 11.4 Custom Cover Art / Icon per Book

- Every book in the library can have a **user-supplied custom image** as its
  cover/icon, shown in the library list, sidebar mini-player, and full-screen
  player.
- Flow: right-click (or long-press) a library row → **"Change Cover"** → file
  picker or drag-and-drop an image onto the row → auto-crop to square → saved
  locally next to that book's data.
- Fallback order when no custom image is set: (1) user-uploaded custom image →
  (2) auto-extracted image from the source PDF/EPUB first page → (3) a generated
  placeholder (solid color block + book title initial, in the app's accent color).
- Custom art must also be embedded into the exported `.m4b`/`.mp3` file's
  metadata (per the base audio pipeline spec), so it travels with the file when
  shared.
- **Data model addition:**
  ```sql
  books(
    ...,
    cover_path,
    cover_source   -- 'custom' | 'extracted' | 'generated'   -- new
  )
  ```
  `cover_source` tells the app whether to leave the cover alone on reprocess
  (`'custom'`) or re-run auto-extraction (`'extracted'`/`'generated'`).

### 11.5 Full-Screen "Now Playing" Mode (Apple Music-style)

Opened by tapping the sidebar mini-player or a dedicated expand icon; closes via
an X in the top-left corner.

- **Background:** a heavily blurred, darkened version of the book's cover art
  fills the entire window behind everything else, consistent with the darker
  theme in §11.3.
- **Main panel:** large square cover art, centered or left-aligned.
  - Below it: book title (equivalent of "track title") and current chapter name
    (equivalent of "artist/album").
  - Scrubber with elapsed / remaining time.
  - Transport controls: skip-back 15s, play/pause, skip-forward 15s,
    previous/next chapter.
  - Speed control docked near the transport controls: the five presets
    (1x/1.25x/1.5x/1.75x/2x) plus the fine ±0.05x stepper from §4/base PRD,
    always reachable without leaving full-screen.
  - Volume slider, top-right, matching the reference layout.
- **Synced text toggle:** an icon button (bottom-right, in the same spot as a
  "lyrics/queue" toggle) swaps the cover-art panel for a **synced text panel** —
  the book's own text scrolling with the currently-spoken word highlighted,
  auto-scrolling as narration plays, rendered in whichever script/language it
  was narrated in (no translation — per §11.2).
  - Tapping any word in this panel seeks playback to that word, same behavior as
    the inline reader view.
- This full-screen mode should also register with the OS media session so
  system-level/lock-screen playback controls work when the app isn't focused
  (already implied by the base PRD's offline/native packaging goals).

---

### 11.6 Chapter Navigation (New — Direct Jump, Not Just Prev/Next)

The previous/next chapter buttons in §11.5 only step one chapter at a time.
That's not enough for a 200k-word book with dozens of chapters — the app also
needs a proper **chapter list you can open and tap to jump straight to any
chapter**, independent of the exported file's chapter markers.

- **Access points:** a "Chapters" icon/button (list icon) in both the inline
  reader view and the full-screen player (§11.5) opens a **chapter list
  overlay**.
- **Chapter list contents:** each row shows chapter index, title, duration,
  and (if narration is still processing) a status indicator — "ready",
  "narrating… 40%", or "not started yet."
- **Tap-to-jump:** tapping any *already-narrated* chapter row immediately
  seeks playback to that chapter's `start_ms` and closes the overlay — no
  need to step through intermediate chapters.
- **Not-yet-narrated chapters:** tapping one either (a) jumps the background
  job queue to prioritize that chapter next, or (b) is disabled with a
  "still processing" state — pick whichever is simpler for v1.1; (a) is the
  better experience if feasible, since it lets the user skip ahead without
  waiting for earlier chapters to finish.
- **Keeps sync intact:** because `chapters.start_ms` is just an offset into
  the same book-level timeline that word-level `word_timestamps` already use
  (§4/§11.5), jumping to a chapter doesn't require recalculating anything —
  the existing highlight-sync logic keeps working immediately after the seek.
- **Also drives export:** the same `chapters.start_ms`/`duration_ms` fields
  are what get written into the `.m4b` file's embedded chapter markers on
  export (§4.5 of the base PRD), so in-app navigation and the exported file's
  chapter list are guaranteed to match.

---

## 12. Open Questions / Future (v2+)

- Cross-language subtitles (e.g. Hindi audio, English captions) — needs a
  translation step (`IndicTrans2` or similar), not in v1.1 scope.
- Additional Indian languages (Indic Parler-TTS already supports ~20) — easy to
  extend the same `language` field/router pattern later if wanted.
- Voice cloning (XTTS-v2 supports this) if a custom narrator voice is desired.
