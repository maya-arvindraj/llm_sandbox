import re


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to make it safe and compatible with Pydantic.
    
    - Normalizes newlines to spaces
    - Removes control characters
    - Strips leading/trailing whitespace
    - Collapses multiple spaces
    
    Args:
        text: Raw user input string
        
    Returns:
        Sanitized string safe for processing
    """
    # Replace newlines and other whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove control characters (except tab/newline which are already normalized)
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text
