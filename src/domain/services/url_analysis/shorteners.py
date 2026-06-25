def has_url_shortener_domain(domain: str, known_shorteners: set[str]) -> bool:
    """Return True when a domain exactly matches a known URL shortener."""
    normalized_domain = domain.strip().strip(".").lower()
    normalized_shorteners = {
        shortener.strip().strip(".").lower()
        for shortener in known_shorteners
    }

    return bool(normalized_domain) and normalized_domain in normalized_shorteners
