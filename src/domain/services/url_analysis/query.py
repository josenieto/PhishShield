from urllib.parse import parse_qsl, urlsplit


def has_suspicious_query_density(url: str, threshold: int) -> bool:
    """Return True when a URL has more query parameters than the threshold."""
    if not url.strip():
        return False

    try:
        query = urlsplit(url).query
    except ValueError:
        return False

    if not query:
        return False

    return len(parse_qsl(query, keep_blank_values=True)) > threshold
