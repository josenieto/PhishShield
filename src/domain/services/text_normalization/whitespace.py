def normalize_whitespace(text: str) -> str:
    """Collapse consecutive whitespace into single spaces and trim boundaries."""
    return " ".join(text.split())
