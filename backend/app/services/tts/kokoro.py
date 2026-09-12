"""Kokoro TTS for English."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        from kokoro import KPipeline

        _pipeline = KPipeline(lang_code="a")
    return _pipeline


def synthesize_english(text: str, output_path: Path, voice: str | None = None) -> None:
    pipeline = _get_pipeline()
    segments: list[np.ndarray] = []
    sample_rate = 24000
    voice_name = voice or "af_heart"

    for _, _, audio in pipeline(text, voice=voice_name, speed=1.0):
        if audio is not None and len(audio) > 0:
            segments.append(np.asarray(audio, dtype=np.float32))

    if not segments:
        raise RuntimeError("Kokoro produced no audio")

    combined = np.concatenate(segments)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output_path), combined, sample_rate)
