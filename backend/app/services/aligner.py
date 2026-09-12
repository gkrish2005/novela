"""WhisperX forced alignment — language-aware."""

from __future__ import annotations

from pathlib import Path

import torch

try:
    _original_torch_load = torch.load
    def _patched_torch_load(*args, **kwargs):
        if "weights_only" in kwargs:
            kwargs["weights_only"] = False
        else:
            kwargs.setdefault("weights_only", False)
        return _original_torch_load(*args, **kwargs)
    torch.load = _patched_torch_load
except Exception:
    pass

_model_cache: dict[str, object] = {}


def _device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _load_model(language: str):
    import whisperx

    device = _device()
    asr_device = "cpu" if device == "mps" else device
    compute_type = "int8" if asr_device == "cpu" else "float16"

    key = f"{language}:{asr_device}"
    if key not in _model_cache:
        _model_cache[key] = whisperx.load_model(
            "large-v2",
            device=asr_device,
            compute_type=compute_type,
            language=language,
        )
    return _model_cache[key]


def align_audio(
    audio_path: Path,
    text: str,
    language: str,
) -> list[dict]:
    """Return word timestamps: word, start_ms, end_ms, char_start, char_end."""
    import whisperx

    device = _device()
    model = _load_model(language)
    audio = whisperx.load_audio(str(audio_path))

    result = model.transcribe(audio, batch_size=4, language=language)
    align_model, metadata = whisperx.load_align_model(
        language_code=language,
        device=device,
    )
    aligned = whisperx.align(
        result["segments"],
        align_model,
        metadata,
        audio,
        device,
        return_char_alignments=False,
    )

    words: list[dict] = []
    cursor = 0
    for segment in aligned.get("segments", []):
        for w in segment.get("words", []):
            word = (w.get("word") or "").strip()
            if not word:
                continue
            start_ms = int(float(w.get("start", 0)) * 1000)
            end_ms = int(float(w.get("end", start_ms / 1000 + 0.1)) * 1000)
            idx = text.find(word, cursor)
            if idx < 0:
                idx = cursor
            char_start = idx
            char_end = idx + len(word)
            cursor = char_end
            words.append(
                {
                    "word": word,
                    "start_ms": start_ms,
                    "end_ms": end_ms,
                    "char_start": char_start,
                    "char_end": char_end,
                    "language": language,
                }
            )
    return words


def fallback_word_timestamps(text: str, duration_ms: int, language: str) -> list[dict]:
    """Evenly distribute words when alignment is unavailable."""
    tokens = text.split()
    if not tokens:
        return []
    slot = max(1, duration_ms // len(tokens))
    words: list[dict] = []
    cursor = 0
    for i, token in enumerate(tokens):
        idx = text.find(token, cursor)
        if idx < 0:
            idx = cursor
        words.append(
            {
                "word": token,
                "start_ms": i * slot,
                "end_ms": (i + 1) * slot,
                "char_start": idx,
                "char_end": idx + len(token),
                "language": language,
            }
        )
        cursor = idx + len(token)
    return words
