"""
Abstract base parser for file parsing services.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union


@dataclass
class ParseResult:
    """Result of parsing a file."""

    text: str
    page_count: int = 1
    character_count: int = 0
    warnings: list[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.character_count == 0:
            self.character_count = len(self.text)


class BaseParser(ABC):
    """Abstract base class for file parsers."""

    SUPPORTED_EXTENSIONS: list[str] = []

    @abstractmethod
    async def parse(self, file_content: bytes, filename: str) -> ParseResult:
        """
        Parse file content and extract text.

        Args:
            file_content: Raw bytes of the file
            filename: Original filename for context

        Returns:
            ParseResult with extracted text and metadata
        """
        pass

    @abstractmethod
    def validate_file(self, file_content: bytes, filename: str) -> tuple[bool, Optional[str]]:
        """
        Validate if the file can be parsed.

        Args:
            file_content: Raw bytes of the file
            filename: Original filename

        Returns:
            Tuple of (is_valid, error_message)
        """
        pass

    def get_extension(self, filename: str) -> str:
        """Get lowercase file extension."""
        return Path(filename).suffix.lower()

    def can_handle(self, filename: str) -> bool:
        """Check if this parser can handle the given file."""
        return self.get_extension(filename) in self.SUPPORTED_EXTENSIONS
