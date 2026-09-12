"""
Common utility functions for text normalization, cleaning, and TTS heading formatting.
"""

from __future__ import annotations

import re


def clean_text_segment(text: str) -> str:
    """Standardizes line endings and removes redundant empty lines."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_heading_for_tts(text: str) -> str:
    """
    Normalizes uppercase words to Title Case to prevent TTS models
    from spelling them out letter-by-letter.
    """
    if text.isupper() and len(text) > 2:
        return text.title()
    return text
