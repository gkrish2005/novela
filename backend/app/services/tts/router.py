"""TTS engine router — Kokoro (en), Indic Parler-TTS (hi)."""

from __future__ import annotations

from pathlib import Path

ENGINES = {
    "en": "kokoro",
    "hi": "indic-parler-tts",
}


def engine_for_language(language: str) -> str:
    return ENGINES.get(language, "kokoro")


def synthesize(text: str, language: str, output_path: Path) -> str:
    engine = engine_for_language(language)
    if engine == "indic-parler-tts":
        from app.services.tts.indic_parler import synthesize_hindi

        synthesize_hindi(text, output_path)
    else:
        from app.services.tts.kokoro import synthesize_english

        synthesize_english(text, output_path)
    return engine
