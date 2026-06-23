def detect_unicode_scripts(text: str) -> set[str]:
    """Return relevant Unicode scripts found in text."""
    scripts: set[str] = set()

    for character in text:
        codepoint = ord(character)

        if _is_latin(codepoint):
            scripts.add("LATIN")
        elif _is_cyrillic(codepoint):
            scripts.add("CYRILLIC")
        elif _is_greek(codepoint):
            scripts.add("GREEK")

    return scripts


def contains_mixed_scripts(text: str) -> bool:
    """Return True when text contains more than one relevant Unicode script."""
    return len(detect_unicode_scripts(text)) > 1


def _is_latin(codepoint: int) -> bool:
    return 0x0041 <= codepoint <= 0x005A or 0x0061 <= codepoint <= 0x007A


def _is_cyrillic(codepoint: int) -> bool:
    return 0x0400 <= codepoint <= 0x04FF


def _is_greek(codepoint: int) -> bool:
    return 0x0370 <= codepoint <= 0x03FF
