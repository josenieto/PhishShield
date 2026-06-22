import unicodedata


def normalize_unicode_text(text: str) -> str:
    """Normalize text using Unicode NFKC compatibility normalization."""
    return unicodedata.normalize("NFKC", text)
