"""
LaTeX file parser - extracts text content from LaTeX documents.
"""

import re
from typing import Optional

from app.core.logging import get_logger
from app.services.parsers.base import BaseParser, ParseResult

logger = get_logger(__name__)


class LaTeXParser(BaseParser):
    """Parser for LaTeX resume files."""

    SUPPORTED_EXTENSIONS = [".tex", ".latex"]
    MAX_FILE_SIZE = 1024 * 1024  # 1MB limit

    # LaTeX commands to remove (but keep their content)
    CONTENT_COMMANDS = [
        "textbf", "textit", "emph", "underline", "texttt",
        "section", "subsection", "subsubsection",
        "title", "author", "date",
        "large", "Large", "LARGE", "huge", "Huge",
        "small", "footnotesize", "scriptsize",
        "centering", "raggedright", "raggedleft",
    ]

    # LaTeX commands to remove entirely (including arguments)
    REMOVE_COMMANDS = [
        "documentclass", "usepackage", "pagestyle", "geometry",
        "setlength", "newcommand", "renewcommand", "definecolor",
        "hypersetup", "fancyhf", "fancyhead", "fancyfoot",
        "begin", "end", "input", "include",
    ]

    async def parse(self, file_content: bytes, filename: str) -> ParseResult:
        """Parse LaTeX file and extract readable text."""
        logger.info("parsing_latex", filename=filename, size=len(file_content))

        # Decode content
        text = self._decode_content(file_content)

        # Extract text from LaTeX
        extracted = self._extract_text(text)

        logger.info("latex_parsed", chars=len(extracted))

        warnings = []
        if "\\begin{tikzpicture}" in text or "\\includegraphics" in text:
            warnings.append("Graphics/diagrams in LaTeX file were not extracted")

        return ParseResult(
            text=extracted,
            page_count=1,
            character_count=len(extracted),
            warnings=warnings,
        )

    def _decode_content(self, content: bytes) -> str:
        """Decode bytes to string."""
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue

        return content.decode("utf-8", errors="ignore")

    def _extract_text(self, latex: str) -> str:
        """Extract readable text from LaTeX source."""
        text = latex

        # Remove comments
        text = re.sub(r"(?<!\\)%.*$", "", text, flags=re.MULTILINE)

        # Extract document body if present
        body_match = re.search(
            r"\\begin\{document\}(.*?)\\end\{document\}",
            text,
            re.DOTALL
        )
        if body_match:
            text = body_match.group(1)

        # Remove preamble commands
        for cmd in self.REMOVE_COMMANDS:
            text = re.sub(rf"\\{cmd}(?:\[[^\]]*\])?\{{[^}}]*\}}", "", text)
            text = re.sub(rf"\\{cmd}(?:\[[^\]]*\])?", "", text)

        # Extract content from commands (keep the argument, remove the command)
        for cmd in self.CONTENT_COMMANDS:
            text = re.sub(rf"\\{cmd}\{{([^}}]*)\}}", r"\1", text)

        # Handle itemize/enumerate
        text = re.sub(r"\\item\s*", "• ", text)

        # Handle href/url
        text = re.sub(r"\\href\{[^}]*\}\{([^}]*)\}", r"\1", text)
        text = re.sub(r"\\url\{([^}]*)\}", r"\1", text)

        # Remove remaining LaTeX commands
        text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?", "", text)

        # Clean up braces
        text = re.sub(r"[{}]", "", text)

        # Clean up whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

        # Clean up lines
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

        return text.strip()

    def validate_file(self, file_content: bytes, filename: str) -> tuple[bool, Optional[str]]:
        """Validate LaTeX file."""
        # Check file extension
        if not self.can_handle(filename):
            return False, f"Invalid file extension: expected .tex or .latex"

        # Check if content is empty
        if not file_content:
            return False, "File is empty"

        # Check file size
        if len(file_content) > self.MAX_FILE_SIZE:
            return False, f"File too large: maximum size is {self.MAX_FILE_SIZE // 1024}KB"

        # Try to decode
        try:
            text = self._decode_content(file_content)
            if not text.strip():
                return False, "File contains no readable text"

            # Basic LaTeX validation - should contain at least one command
            if "\\" not in text:
                return False, "File does not appear to be valid LaTeX"

        except Exception as e:
            return False, f"Failed to read file: {str(e)}"

        return True, None
