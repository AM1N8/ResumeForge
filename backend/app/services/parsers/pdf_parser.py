"""
PDF file parser using pdfplumber with pypdf fallback.
"""

import io
from typing import Optional

import pdfplumber
from pypdf import PdfReader

from app.core.logging import get_logger
from app.services.parsers.base import BaseParser, ParseResult

logger = get_logger(__name__)


class PDFParser(BaseParser):
    """Parser for PDF resume files."""

    SUPPORTED_EXTENSIONS = [".pdf"]

    async def parse(self, file_content: bytes, filename: str) -> ParseResult:
        """
        Parse PDF and extract text using pdfplumber.
        Falls back to pypdf if pdfplumber fails.
        """
        logger.info("parsing_pdf", filename=filename, size=len(file_content))

        # Try pdfplumber first (better layout preservation)
        try:
            result = self._parse_with_pdfplumber(file_content)
            logger.info("pdf_parsed_pdfplumber", pages=result.page_count, chars=result.character_count)
            return result
        except Exception as e:
            logger.warning("pdfplumber_failed", error=str(e), filename=filename)

        # Fallback to pypdf
        try:
            result = self._parse_with_pypdf(file_content)
            result.warnings.append("Parsed with fallback parser - some formatting may be lost")
            logger.info("pdf_parsed_pypdf", pages=result.page_count, chars=result.character_count)
            return result
        except Exception as e:
            logger.error("pdf_parse_failed", error=str(e), filename=filename)
            raise ValueError(f"Failed to parse PDF: {str(e)}")

    def _parse_with_pdfplumber(self, file_content: bytes) -> ParseResult:
        """Parse PDF using pdfplumber for better layout handling."""
        text_parts = []
        page_count = 0

        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            page_count = len(pdf.pages)

            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        full_text = "\n\n".join(text_parts)

        if not full_text.strip():
            raise ValueError("No text could be extracted from PDF")

        return ParseResult(
            text=full_text.strip(),
            page_count=page_count,
            character_count=len(full_text),
        )

    def _parse_with_pypdf(self, file_content: bytes) -> ParseResult:
        """Parse PDF using pypdf as fallback."""
        text_parts = []

        reader = PdfReader(io.BytesIO(file_content))
        page_count = len(reader.pages)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        full_text = "\n\n".join(text_parts)

        if not full_text.strip():
            raise ValueError("No text could be extracted from PDF")

        return ParseResult(
            text=full_text.strip(),
            page_count=page_count,
            character_count=len(full_text),
        )

    def validate_file(self, file_content: bytes, filename: str) -> tuple[bool, Optional[str]]:
        """Validate PDF file."""
        # Check file extension
        if not self.can_handle(filename):
            return False, f"Invalid file extension: expected .pdf"

        # Check if content is empty
        if not file_content:
            return False, "File is empty"

        # Check PDF magic bytes
        if not file_content.startswith(b"%PDF"):
            return False, "File does not appear to be a valid PDF"

        # Try to open the PDF to check for corruption/password
        try:
            reader = PdfReader(io.BytesIO(file_content))
            if reader.is_encrypted:
                return False, "PDF is password protected"
            # Try to access pages to check readability
            _ = len(reader.pages)
        except Exception as e:
            return False, f"PDF validation failed: {str(e)}"

        return True, None
