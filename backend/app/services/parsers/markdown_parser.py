"""
Markdown file parser.
"""

from typing import Optional

from app.core.logging import get_logger
from app.services.parsers.base import BaseParser, ParseResult

logger = get_logger(__name__)


class MarkdownParser(BaseParser):
    """Parser for Markdown resume files."""

    SUPPORTED_EXTENSIONS = [".md", ".markdown"]
    MAX_FILE_SIZE = 1024 * 1024  # 1MB limit for text files

    async def parse(self, file_content: bytes, filename: str) -> ParseResult:
        """Parse Markdown file and extract text."""
        logger.info("parsing_markdown", filename=filename, size=len(file_content))

        # Decode with UTF-8 (primary) and fallbacks
        text = self._decode_content(file_content)

        # Clean up the text
        text = self._clean_text(text)

        logger.info("markdown_parsed", chars=len(text))

        return ParseResult(
            text=text,
            page_count=1,
            character_count=len(text),
        )

    def _decode_content(self, content: bytes) -> str:
        """Decode bytes to string with encoding fallbacks."""
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue

        # Last resort - decode with errors ignored
        return content.decode("utf-8", errors="ignore")

    def _clean_text(self, text: str) -> str:
        """Clean up the markdown text."""
        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove excessive blank lines
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")

        return text.strip()

    def validate_file(self, file_content: bytes, filename: str) -> tuple[bool, Optional[str]]:
        """Validate Markdown file."""
        # Check file extension
        if not self.can_handle(filename):
            return False, f"Invalid file extension: expected .md or .markdown"

        # Check if content is empty
        if not file_content:
            return False, "File is empty"

        # Check file size
        if len(file_content) > self.MAX_FILE_SIZE:
            return False, f"File too large: maximum size is {self.MAX_FILE_SIZE // 1024}KB"

        # Try to decode the content
        try:
            text = self._decode_content(file_content)
            if not text.strip():
                return False, "File contains no readable text"
        except Exception as e:
            return False, f"Failed to read file: {str(e)}"

        return True, None
