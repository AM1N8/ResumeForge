"""Parser factory and registry."""

from pathlib import Path
from typing import Optional

from app.services.parsers.base import BaseParser, ParseResult
from app.services.parsers.pdf_parser import PDFParser
from app.services.parsers.markdown_parser import MarkdownParser
from app.services.parsers.latex_parser import LaTeXParser


class ParserFactory:
    """Factory for getting appropriate parser for a file type."""

    _parsers: list[BaseParser] = [
        PDFParser(),
        MarkdownParser(),
        LaTeXParser(),
    ]

    @classmethod
    def get_parser(cls, filename: str) -> Optional[BaseParser]:
        """Get the appropriate parser for a file."""
        for parser in cls._parsers:
            if parser.can_handle(filename):
                return parser
        return None

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get all supported file extensions."""
        extensions = []
        for parser in cls._parsers:
            extensions.extend(parser.SUPPORTED_EXTENSIONS)
        return extensions

    @classmethod
    def is_supported(cls, filename: str) -> bool:
        """Check if a file type is supported."""
        return cls.get_parser(filename) is not None


__all__ = [
    "BaseParser",
    "ParseResult",
    "PDFParser",
    "MarkdownParser",
    "LaTeXParser",
    "ParserFactory",
]
