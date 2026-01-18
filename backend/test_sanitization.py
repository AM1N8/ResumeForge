# Self-contained test for the sanitization logic
def sanitize_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\x00", "")
    return "".join(c for c in text if c.isprintable() or c in "\n\r\t")

def test_sanitization():
    test_data = [
        ("Normal text", "Normal text"),
        ("Text with null\x00 byte", "Text with null byte"),
        ("UTF-16 ish\x00 \x00s\x00t\x00r\x00i\x00n\x00g", "UTF-16 ish string"),
        ("Newline\nand\rtab\tkeep", "Newline\nand\rtab\tkeep"),
        ("Control\x01\x02 characters", "Control characters"),
    ]
    
    for input_str, expected in test_data:
        result = sanitize_text(input_str)
        print(f"Input: {repr(input_str)}")
        print(f"Result: {repr(result)}")
        assert result == expected, f"Failed for {repr(input_str)}. Got {repr(result)}"
    
    print("\nAll sanitization tests passed!")

if __name__ == "__main__":
    test_sanitization()
