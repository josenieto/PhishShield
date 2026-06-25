from urllib.parse import urlsplit


def has_embedded_credentials(url: str) -> bool:
    """Return True when a URL authority contains embedded credentials."""
    if not url.strip():
        return False

    try:
        parsed_url = urlsplit(url)
        username = parsed_url.username
    except ValueError:
        return False

    return parsed_url.scheme.lower() in {"http", "https"} and username is not None
