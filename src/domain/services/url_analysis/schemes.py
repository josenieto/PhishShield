SUSPICIOUS_URL_SCHEMES: frozenset[str] = frozenset(
    {
        "javascript",
        "data",
        "file",
        "vbscript",
    }
)


def is_url_scheme_allowed(scheme: str, allowed_schemes: set[str]) -> bool:
    """Return True when a URL scheme is present in the allowed set."""
    normalized_scheme = scheme.strip().lower()
    normalized_allowed_schemes = {
        allowed_scheme.strip().lower()
        for allowed_scheme in allowed_schemes
    }

    return bool(normalized_scheme) and normalized_scheme in normalized_allowed_schemes


def is_suspicious_url_scheme(scheme: str) -> bool:
    """Return True when a URL scheme is commonly abused in phishing links."""
    return scheme.strip().lower() in SUSPICIOUS_URL_SCHEMES
