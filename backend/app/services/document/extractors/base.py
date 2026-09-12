"""
Base interface for document extractors.
Every source extractor transforms arbitrary file inputs into a NormalizedDocument.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from app.services.document.models import NormalizedDocument


class BaseExtractor(ABC):
    """Abstract base class for all document format extractors."""

    @abstractmethod
    def can_handle(self, source: Union[str, Path, bytes]) -> bool:
        """Determines whether this extractor can parse the given source."""
        pass

    @abstractmethod
    def extract(self, source: Union[str, Path, bytes], title_hint: str = "") -> NormalizedDocument:
        """Extracts content, layout, TOC, and metadata into a NormalizedDocument."""
        pass
