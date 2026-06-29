def normalize_hash(value: str) -> str:
    """Return a textual hash normalized for format checks."""
    return value.strip().lower()


def is_empty_hash(value: str) -> bool:
    """Return True when a textual hash is empty after normalization."""
    return normalize_hash(value) == ""


def is_valid_sha256(value: str) -> bool:
    """Return True when a textual hash has valid SHA-256 format."""
    normalized_value = normalize_hash(value)

    if len(normalized_value) != 64:
        return False

    return all(
        character in "0123456789abcdef"
        for character in normalized_value
    )
