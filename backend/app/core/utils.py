"""
Core utility functions for the application.
"""

def sanitize_text(text: str) -> str:
    """
    Sanitize text for LLM consumption.
    Strips null bytes and non-printable control characters except whitespace.
    
    This is critical for preventing LLM API errors and tokenization issues
    caused by invalid characters in source data (e.g., GitHub READMEs).
    """
    if not text:
        return ""
    
    # Remove null bytes explicitly first
    text = text.replace("\x00", "")
    
    # Filter for printable characters and standard whitespace
    # c.isprintable() is good, but we must explicitly allow \n \r \t 
    # as they are often not considered 'printable' in some contexts
    # but are essential for text structure.
    return "".join(c for c in text if c.isprintable() or c in "\n\r\t")
