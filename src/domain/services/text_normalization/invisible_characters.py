SUSPICIOUS_INVISIBLE_CHARACTERS: frozenset[str] = frozenset(
    {
        "\u200b",
        "\u200c",
        "\u200d",
    }
)


def contains_invisible_chars(text: str) -> bool:
    """Return True when text contains suspicious invisible Unicode characters."""
    return any(character in SUSPICIOUS_INVISIBLE_CHARACTERS for character in text)


def strip_invisible_chars(text: str) -> str:
    """Remove suspicious invisible Unicode characters from text."""
    return "".join(
        character for character in text
        if character not in SUSPICIOUS_INVISIBLE_CHARACTERS
    )
