CONFUSABLE_CHARACTERS: frozenset[str] = frozenset(
    {
        "\u0430",
        "\u0435",
        "\u043e",
        "\u0440",
        "\u0441",
        "\u0443",
        "\u0445",
        "\u03b1",
        "\u03bf",
    }
)


def contains_confusable_characters(text: str) -> bool:
    """Return True when text contains phishing-relevant confusable characters."""
    return bool(find_confusable_characters(text))


def find_confusable_characters(text: str) -> list[str]:
    """Return phishing-relevant confusable characters in discovery order."""
    return [
        character
        for character in text
        if character in CONFUSABLE_CHARACTERS
    ]
