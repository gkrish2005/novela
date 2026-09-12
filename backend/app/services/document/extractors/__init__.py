"""
Extractors package for Novela's Universal Document Ingestion Pipeline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

from app.services.document.extractors.base import BaseExtractor
from app.services.document.extractors.docx import DOCXExtractor
from app.services.document.extractors.epub import EPUBExtractor
from app.services.document.extractors.markdown import MarkdownExtractor
from app.services.document.extractors.pdf import PDFExtractor
from app.services.document.extractors.txt import TXTExtractor


def get_extractor(source: Union[str, Path, bytes]) -> BaseExtractor:
    """Selects the appropriate extractor for the given file or stream."""
    extractors: list[BaseExtractor] = [
        PDFExtractor(),
        EPUBExtractor(),
        DOCXExtractor(),
        MarkdownExtractor(),
        TXTExtractor(),
    ]
    for ext in extractors:
        if ext.can_handle(source):
            return ext
    # Default fallback to TXT
    return TXTExtractor()


__all__ = [
    "BaseExtractor",
    "PDFExtractor",
    "EPUBExtractor",
    "DOCXExtractor",
    "MarkdownExtractor",
    "TXTExtractor",
    "get_extractor",
]
